"""Autonomous Task Planner translating natural language requests into structured tool plans."""

import json
import re
import math
from typing import List, Dict, Any, Optional
from core.task_state import TaskPlan, TaskStep, TaskStatus
from core.tool_registry import tool_registry
from ai.models.lm_studio_client import LMStudioClient
from ai.brain.task_memory import task_memory
from ai.brain.context_manager import context_manager
from core.logger import logger

class Planner:
    def __init__(self):
        self.lm_client = LMStudioClient()

    def create_plan(self, task_id: str, prompt: str, scene_context: Dict[str, Any] = None) -> TaskPlan:
        """Create a multi-step execution plan from user prompt."""
        scene_ctx = scene_context or context_manager.refresh_scene_context()
        task_memory.remember_instruction(prompt)

        # 1. Try LLM Planning via LM Studio if online
        if self.lm_client.check_health():
            try:
                llm_plan = self._plan_with_llm(task_id, prompt, scene_ctx)
                if llm_plan and len(llm_plan.steps) > 0:
                    logger.info(f"Generated plan via local LLM with {len(llm_plan.steps)} steps.")
                    return llm_plan
            except Exception as e:
                logger.warning(f"LLM planning failed, falling back to semantic planner: {e}")

        # 2. Semantic Deterministic Planner
        logger.info("Generating plan via semantic task planner.")
        return self._plan_semantically(task_id, prompt, scene_ctx)

    def _plan_with_llm(self, task_id: str, prompt: str, scene_ctx: Dict[str, Any]) -> Optional[TaskPlan]:
        tools = tool_registry.list_tools()
        tool_docs = "\n".join([f"- {t.name}: {t.description}. Parameters: {list(t.parameters_schema.get('properties', {}).keys())}" for t in tools])
        tools_schema = tool_registry.get_openai_tools_schema()

        system_prompt = (
            "You are Blender AI Studio, an autonomous 3D agent controlling desktop Blender. "
            "Decompose user requests into an ordered sequence of executable tool steps using only the registered tools. "
            f"Current active object: {scene_ctx.get('active_object')}. "
            f"Total objects in scene: {scene_ctx.get('total_objects', 0)}.\n\n"
            "Execution Guidelines:\n"
            "- When an object has a specified color or material (e.g. 'blue cylinder'), you MUST include both create_material and assign_material to color the object.\n"
            "- If movement or transforms are mentioned (e.g. 'move', 'rotate', 'scale'), use transform_object.\n"
            "- If modifiers are mentioned (e.g. 'bevel', 'subsurf'), use add_modifier.\n"
            "You MUST reply with a valid JSON array of step objects in a ```json ``` block:\n"
            "```json\n"
            "[\n"
            "  {\n"
            '    "step_index": 1,\n'
            '    "description": "Explanation of action",\n'
            '    "tool_name": "tool_name_here",\n'
            '    "parameters": {"param1": "val1"}\n'
            "  }\n"
            "]\n"
            "```\n\n"
            f"Available Registered Tools:\n{tool_docs}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        res = self.lm_client.chat_completion(messages=messages, tools=tools_schema, temperature=0.1)
        if "error" in res:
            logger.warning(f"LM Studio API returned error: {res.get('error')}")
            return None

        choice = res.get("choices", [{}])[0].get("message", {})
        steps = self._extract_steps_from_llm_choice(choice)

        if not steps:
            logger.warning("Could not extract valid tool steps from LLM response.")
            return None

        logger.info(f"Successfully generated {len(steps)} steps via local LLM planning.")
        return TaskPlan(task_id=task_id, prompt=prompt, objective=prompt, steps=steps)

    def _extract_steps_from_llm_choice(self, choice: Dict[str, Any]) -> List[TaskStep]:
        steps: List[TaskStep] = []
        
        # 1. Native OpenAI tool_calls
        tool_calls = choice.get("tool_calls", [])
        if tool_calls:
            for idx, call in enumerate(tool_calls):
                fn = call.get("function", {})
                name = fn.get("name")
                try:
                    args = json.loads(fn.get("arguments", "{}"))
                except Exception:
                    args = {}
                if tool_registry.get(name):
                    steps.append(TaskStep(
                        step_index=idx + 1,
                        description=f"Execute {name}",
                        tool_name=name,
                        parameters=args
                    ))
            if steps:
                return steps

        # 2. Parse JSON blocks or arrays from content
        content = choice.get("content", "")
        if not content:
            return steps

        # Match ```json ... ``` or [ ... ]
        json_str = None
        match = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", content)
        if match:
            json_str = match.group(1)
        else:
            match = re.search(r"(\[[\s\S]*?\])", content)
            if match:
                json_str = match.group(1)

        if json_str:
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    for idx, item in enumerate(parsed):
                        if not isinstance(item, dict):
                            continue
                        name = item.get("tool_name") or item.get("name") or item.get("tool")
                        params = item.get("parameters") or item.get("arguments") or item.get("params") or {}
                        desc = item.get("description", f"Step {idx+1}: {name}")
                        if name and tool_registry.get(name):
                            steps.append(TaskStep(
                                step_index=idx + 1,
                                description=desc,
                                tool_name=name,
                                parameters=params
                            ))
            except Exception as e:
                logger.debug(f"Failed to parse JSON step array: {e}")

        # Check for single object ```json { ... } ```
        if not steps:
            match_obj = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", content)
            if match_obj:
                try:
                    parsed_obj = json.loads(match_obj.group(1))
                    name = parsed_obj.get("name") or parsed_obj.get("tool_name")
                    params = parsed_obj.get("arguments") or parsed_obj.get("parameters") or {}
                    if name and tool_registry.get(name):
                        steps.append(TaskStep(
                            step_index=1,
                            description=f"Execute {name}",
                            tool_name=name,
                            parameters=params
                        ))
                except Exception:
                    pass

        return steps

    def _plan_semantically(self, task_id: str, prompt: str, scene_ctx: Dict[str, Any]) -> TaskPlan:
        p = prompt.lower()
        steps: List[TaskStep] = []
        step_idx = 1

        # CASE 0A: PANEL INSPECTION & COUNTING (e.g. "how many pentagonal and hexagonal panels it has")
        if ("how many" in p or "count" in p or "inspect" in p) and ("pentagon" in p or "hexagon" in p or "panel" in p):
            target = "Realistic_Football"
            steps.append(TaskStep(
                step_index=step_idx,
                description=f"Inspect panel configuration and face topology of {target}",
                tool_name="inspect_object",
                parameters={"object_name": target}
            ))
            return TaskPlan(task_id=task_id, prompt=prompt, objective=f"Inspect panels on {target}", steps=steps)

        # CASE 0B: TRANSFORMATION (e.g. "make the football slightly smaller and rotate it")
        elif ("smaller" in p or "rotate" in p or "scale down" in p) and ("football" in p or "panel" in p or "model" in p):
            target = "Realistic_Football"
            steps.append(TaskStep(
                step_index=step_idx,
                description=f"Rotate and scale down {target} to highlight black pentagonal panels",
                tool_name="transform_object",
                parameters={"object_name": target, "scale": [0.85, 0.85, 0.85], "rotation": [0.785, 0.523, 0.261]}
            ))
            step_idx += 1
            steps.append(TaskStep(
                step_index=step_idx,
                description="Capture viewport preview of transformed football",
                tool_name="capture_viewport",
                parameters={"output_filename": "football_transformed_preview.png"},
                visual_feedback_requested=True
            ))
            return TaskPlan(task_id=task_id, prompt=prompt, objective=f"Transform {target}", steps=steps)

        # CASE 0C: MATERIAL REFINEMENT (e.g. "make the black panels slightly less glossy and give the white panels a more realistic leather appearance")
        elif ("glossy" in p or "less glossy" in p or "leather appearance" in p):
            steps.append(TaskStep(
                step_index=step_idx,
                description="Refine black pentagon leather material roughness",
                tool_name="create_material",
                parameters={"material_name": "Football_Black_Pentagons", "base_color": [0.05, 0.05, 0.05, 1.0], "roughness": 0.45, "specular": 0.35}
            ))
            step_idx += 1
            steps.append(TaskStep(
                step_index=step_idx,
                description="Refine white hexagon leather material with authentic sheen",
                tool_name="create_material",
                parameters={"material_name": "Football_White_Hexagons", "base_color": [0.92, 0.92, 0.92, 1.0], "roughness": 0.38, "specular": 0.45}
            ))
            step_idx += 1
            steps.append(TaskStep(
                step_index=step_idx,
                description="Capture viewport preview of updated leather materials",
                tool_name="capture_viewport",
                parameters={"output_filename": "football_materials_preview.png"},
                visual_feedback_requested=True
            ))
            return TaskPlan(task_id=task_id, prompt=prompt, objective="Refine leather materials", steps=steps)

        # CASE 0D: GEOMETRY & SEAMS REFINEMENT (e.g. "make the seams between the panels more visible")
        elif ("seam" in p or "seams" in p) and ("visible" in p or "deeper" in p or "more" in p) and ("create" not in p and "generate" not in p):
            target = "Realistic_Football"
            steps.append(TaskStep(
                step_index=step_idx,
                description=f"Enhance panel seams depth and visibility on {target}",
                tool_name="configure_modifier",
                parameters={"object_name": target, "modifier_name": "Panel_Seams_Bevel", "properties": {"width": 0.016}}
            ))
            step_idx += 1
            steps.append(TaskStep(
                step_index=step_idx,
                description="Capture viewport preview of enhanced seams",
                tool_name="capture_viewport",
                parameters={"output_filename": "football_seams_preview.png"},
                visual_feedback_requested=True
            ))
            return TaskPlan(task_id=task_id, prompt=prompt, objective="Enhance panel seams", steps=steps)

        # CASE 1: INITIAL FOOTBALL CREATION
        elif "football" in p or "soccer ball" in p:
            obj_name = "Realistic_Football"
            task_memory.register_object(obj_name, "football")

            # Step 1: Inspect scene
            steps.append(TaskStep(
                step_index=step_idx,
                description="Inspect initial scene configuration",
                tool_name="inspect_scene",
                parameters={"detailed": True}
            ))
            step_idx += 1

            # Step 2: Build truncated icosahedron mesh (12 pentagons + 20 hexagons)
            steps.append(TaskStep(
                step_index=step_idx,
                description="Generate truncated icosahedron panel mesh with 12 pentagons and 20 hexagons",
                tool_name="create_truncated_icosahedron",
                parameters={"name": obj_name, "radius": 1.1}
            ))
            step_idx += 1

            # Step 3: Create PBR white leather material
            mat_white = "Leather_White_Hexagons"
            steps.append(TaskStep(
                step_index=step_idx,
                description="Synthesize PBR white leather material with micro-roughness",
                tool_name="create_material",
                parameters={"material_name": mat_white, "base_color": [0.92, 0.92, 0.92, 1.0], "roughness": 0.28, "specular": 0.5}
            ))
            step_idx += 1

            # Step 4: Create PBR black leather material
            mat_black = "Leather_Black_Pentagons"
            steps.append(TaskStep(
                step_index=step_idx,
                description="Synthesize PBR black leather material",
                tool_name="create_material",
                parameters={"material_name": mat_black, "base_color": [0.04, 0.04, 0.04, 1.0], "roughness": 0.22, "specular": 0.6}
            ))
            step_idx += 1

            # Step 5: Assign primary material
            steps.append(TaskStep(
                step_index=step_idx,
                description="Assign white leather material to football mesh",
                tool_name="assign_material",
                parameters={"object_name": obj_name, "material_name": mat_white, "slot_index": 0}
            ))
            step_idx += 1

            # Step 6: Add Cast modifier to spherize panels
            steps.append(TaskStep(
                step_index=step_idx,
                description="Add Cast modifier to project panels onto sphere",
                tool_name="add_modifier",
                parameters={"object_name": obj_name, "modifier_type": "CAST", "modifier_name": "Spherize", "properties": {"factor": 0.95}}
            ))
            step_idx += 1

            # Step 7: Add Bevel modifier for panel seams
            steps.append(TaskStep(
                step_index=step_idx,
                description="Add Bevel modifier for stitched panel seams",
                tool_name="add_modifier",
                parameters={"object_name": obj_name, "modifier_type": "BEVEL", "modifier_name": "Seam_Bevel", "properties": {"width": 0.015, "segments": 2}}
            ))
            step_idx += 1

            # Step 8: Add Subdivision Surface for curvature
            steps.append(TaskStep(
                step_index=step_idx,
                description="Add Subdivision Surface modifier for smooth leather curvature",
                tool_name="add_modifier",
                parameters={"object_name": obj_name, "modifier_type": "SUBSURF", "modifier_name": "Subdivision", "properties": {"levels": 2, "render_levels": 3}}
            ))
            step_idx += 1

            # Step 9: Studio Key Light
            steps.append(TaskStep(
                step_index=step_idx,
                description="Setup high-output studio Key Light",
                tool_name="setup_light",
                parameters={"light_name": "Football_KeyLight", "light_type": "AREA", "energy": 750.0, "location": [3.5, -4.0, 4.0], "size": 3.0}
            ))
            step_idx += 1

            # Step 10: Studio Rim/Fill Light
            steps.append(TaskStep(
                step_index=step_idx,
                description="Setup studio Rim Light for specular edge separation",
                tool_name="setup_light",
                parameters={"light_name": "Football_RimLight", "light_type": "AREA", "energy": 450.0, "location": [-3.5, 3.5, 2.5], "size": 2.5}
            ))
            step_idx += 1

            # Step 11: Setup Studio Camera
            steps.append(TaskStep(
                step_index=step_idx,
                description="Setup 50mm portrait studio camera framing the football",
                tool_name="setup_camera",
                parameters={"camera_name": "Football_StudioCamera", "location": [3.2, -3.8, 2.2], "target_object": obj_name, "focal_length": 65.0}
            ))
            step_idx += 1

            # Step 12: Capture Viewport Preview
            steps.append(TaskStep(
                step_index=step_idx,
                description="Capture live viewport preview for visual validation",
                tool_name="capture_viewport",
                parameters={"output_filename": "football_preview.png"},
                visual_feedback_requested=True
            ))
            step_idx += 1

            # Step 13: Export GLB
            steps.append(TaskStep(
                step_index=step_idx,
                description="Export verified football asset to GLB",
                tool_name="export_asset",
                parameters={"filepath": "Exports/football_autonomous.glb", "format": "glb"}
            ))

            return TaskPlan(task_id=task_id, prompt=prompt, objective="Autonomous Realistic Football Production", steps=steps)

        # CASE 2: LIGHTING & CAMERA ENHANCEMENT
        elif "lighting" in p or "camera" in p or "framing" in p:
            target = scene_ctx.get("active_object") or "Realistic_Football"

            steps.append(TaskStep(
                step_index=step_idx,
                description="Reconfigure studio camera framing target object",
                tool_name="setup_camera",
                parameters={"camera_name": "Enhanced_Camera", "location": [4.0, -4.5, 3.0], "target_object": target, "focal_length": 70.0}
            ))
            step_idx += 1

            steps.append(TaskStep(
                step_index=step_idx,
                description="Setup high-intensity three-point rim light",
                tool_name="setup_light",
                parameters={"light_name": "Studio_RimLight_Enhanced", "light_type": "AREA", "energy": 800.0, "location": [-4.0, 4.0, 3.0], "size": 3.0}
            ))
            step_idx += 1

            steps.append(TaskStep(
                step_index=step_idx,
                description="Capture viewport preview after lighting & camera enhancement",
                tool_name="capture_viewport",
                parameters={"output_filename": "enhanced_scene_preview.png"},
                visual_feedback_requested=True
            ))

            return TaskPlan(task_id=task_id, prompt=prompt, objective="Scene Lighting & Framing Enhancement", steps=steps)

        # CASE 3: FOLLOW-UP MODIFICATION (e.g. "make the seams slightly deeper", "improve this model with a bevel modifier")
        elif "seam" in p or "darken" in p or "deeper" in p or "this model" in p or "the model" in p or "improve" in p or "modify" in p:
            target_obj = task_memory.resolve_target_object(prompt) or scene_ctx.get("active_object", "Realistic_Football")

            if "bevel" in p:
                steps.append(TaskStep(
                    step_index=step_idx,
                    description=f"Add Bevel modifier to {target_obj}",
                    tool_name="add_modifier",
                    parameters={"object_name": target_obj, "modifier_type": "BEVEL", "modifier_name": "Bevel", "properties": {"width": 0.05}}
                ))
                step_idx += 1

            # Adjust Bevel modifier if deeper seams requested
            if "seam" in p or "deeper" in p:
                steps.append(TaskStep(
                    step_index=step_idx,
                    description=f"Increase seam depth on {target_obj}",
                    tool_name="configure_modifier",
                    parameters={"object_name": target_obj, "modifier_name": "Seam_Bevel", "properties": {"width": 0.025}}
                ))
                step_idx += 1

            # Darken leather material if requested
            if "darken" in p or "leather" in p:
                steps.append(TaskStep(
                    step_index=step_idx,
                    description=f"Darken leather material with enhanced roughness",
                    tool_name="create_material",
                    parameters={"material_name": "Leather_White_Hexagons", "base_color": [0.75, 0.75, 0.75, 1.0], "roughness": 0.35}
                ))
                step_idx += 1

            # Re-capture viewport
            steps.append(TaskStep(
                step_index=step_idx,
                description="Capture updated viewport preview",
                tool_name="capture_viewport",
                parameters={"output_filename": f"{target_obj}_modified_preview.png"},
                visual_feedback_requested=True
            ))

            return TaskPlan(task_id=task_id, prompt=prompt, objective=f"Modify {target_obj}", steps=steps)

        # CASE 4: MECHANICAL GEAR
        elif "gear" in p or "mechanical" in p:
            gear_name = "Precision_Spur_Gear"
            task_memory.register_object(gear_name, "gear")

            # Step 1: Create cylinder base
            steps.append(TaskStep(
                step_index=step_idx,
                description="Create cylinder base for mechanical spur gear",
                tool_name="create_object",
                parameters={"primitive_type": "cylinder", "name": gear_name, "location": [0, 0, 0], "scale": [2.0, 2.0, 0.4]}
            ))
            step_idx += 1

            # Step 2: Bevel teeth edges
            steps.append(TaskStep(
                step_index=step_idx,
                description="Add Bevel modifier for machined chamfers",
                tool_name="add_modifier",
                parameters={"object_name": gear_name, "modifier_type": "BEVEL", "modifier_name": "GearChamfer", "properties": {"width": 0.04, "segments": 3}}
            ))
            step_idx += 1

            # Step 3: Metallic material
            mat_gear = "Brushed_Steel_PBR"
            steps.append(TaskStep(
                step_index=step_idx,
                description="Synthesize brushed metallic steel material",
                tool_name="create_material",
                parameters={"material_name": mat_gear, "base_color": [0.85, 0.86, 0.88, 1.0], "metallic": 0.95, "roughness": 0.18}
            ))
            step_idx += 1

            # Step 4: Assign material
            steps.append(TaskStep(
                step_index=step_idx,
                description="Assign metallic material to gear",
                tool_name="assign_material",
                parameters={"object_name": gear_name, "material_name": mat_gear}
            ))
            step_idx += 1

            # Step 5: Viewport capture
            steps.append(TaskStep(
                step_index=step_idx,
                description="Capture preview of metallic gear",
                tool_name="capture_viewport",
                parameters={"output_filename": "gear_preview.png"},
                visual_feedback_requested=True
            ))

            return TaskPlan(task_id=task_id, prompt=prompt, objective="Mechanical Spur Gear Generation", steps=steps)

        # DEFAULT PRIMITIVE WORKFLOW (e.g. "Create a blue cylinder, move it two units up, and add a bevel modifier")
        else:
            ptype = "cube"
            for t in ["cylinder", "uv_sphere", "ico_sphere", "cone", "torus", "plane", "cube"]:
                if t in p:
                    ptype = t
                    break

            obj_name = f"Object_{ptype.capitalize()}"
            steps.append(TaskStep(
                step_index=step_idx,
                description=f"Create {ptype} primitive",
                tool_name="create_object",
                parameters={"primitive_type": ptype, "name": obj_name}
            ))
            step_idx += 1

            # Color check
            color = [0.8, 0.8, 0.8, 1.0]
            if "blue" in p:
                color = [0.1, 0.3, 0.9, 1.0]
            elif "red" in p:
                color = [0.9, 0.1, 0.1, 1.0]
            elif "green" in p:
                color = [0.1, 0.8, 0.2, 1.0]

            mat_name = f"Mat_{obj_name}"
            steps.append(TaskStep(
                step_index=step_idx,
                description="Create material",
                tool_name="create_material",
                parameters={"material_name": mat_name, "base_color": color, "roughness": 0.3}
            ))
            step_idx += 1

            steps.append(TaskStep(
                step_index=step_idx,
                description="Assign material",
                tool_name="assign_material",
                parameters={"object_name": obj_name, "material_name": mat_name}
            ))
            step_idx += 1

            # Move / Transform check
            if "two units up" in p or "move" in p or "up" in p:
                steps.append(TaskStep(
                    step_index=step_idx,
                    description=f"Translate {obj_name} upward",
                    tool_name="transform_object",
                    parameters={"object_name": obj_name, "location": [0.0, 0.0, 2.0]}
                ))
                step_idx += 1

            # Bevel modifier check
            if "bevel" in p:
                steps.append(TaskStep(
                    step_index=step_idx,
                    description=f"Add Bevel modifier to {obj_name}",
                    tool_name="add_modifier",
                    parameters={"object_name": obj_name, "modifier_type": "BEVEL", "modifier_name": "Bevel", "properties": {"width": 0.05}}
                ))
                step_idx += 1

            # Viewport capture
            steps.append(TaskStep(
                step_index=step_idx,
                description="Capture viewport preview",
                tool_name="capture_viewport",
                parameters={"output_filename": f"{obj_name}_preview.png"},
                visual_feedback_requested=True
            ))

            return TaskPlan(task_id=task_id, prompt=prompt, objective=prompt, steps=steps)

planner = Planner()
