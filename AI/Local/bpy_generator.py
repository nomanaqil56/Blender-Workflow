"""
Blender AI Studio - Procedural BPY Script Generator
Synthesizes, validates, and refines Blender Python (bpy) procedural scripts
from natural language descriptions.
"""

import sys
import re
import ast
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from AI.Local.lm_studio_client import LMStudioClient
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from AI.Local.lm_studio_client import LMStudioClient

SYSTEM_PROMPT_BPY = """You are a senior Blender Python (bpy) technical artist and procedural developer.
Write complete, executable, clean Blender Python script that creates the requested 3D asset or scene.

Rules:
1. Output ONLY executable Python code inside a single ```python ... ``` block.
2. Target modern Blender (4.x / 5.x). Use bpy.data and bpy.ops safely.
3. Use procedural techniques: modifiers (Subdivision, Bevel, Array, Boolean, Solidify), math, and mathutils.
4. Clean up any existing objects or create into a dedicated new Collection.
5. Setup proper PBR Principled BSDF materials (base_color, metallic, roughness).
6. Ensure normals are consistent and scale is applied (bpy.ops.object.transform_apply).
7. Do not import third-party modules outside standard Python and Blender (math, mathutils, random, bmesh).
"""


class BpyGenerator:
    """Generates and validates procedural Blender modeling scripts."""

    def __init__(self, lm_client: Optional[LMStudioClient] = None):
        self.lm_client = lm_client or LMStudioClient()

    @staticmethod
    def extract_code(text: str) -> str:
        """Extracts python code from markdown code fences or returns bare text."""
        match = re.search(r"```(?:python)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    @staticmethod
    def validate_syntax(code: str) -> Dict[str, Any]:
        """Validates python syntax via AST parsing."""
        try:
            ast.parse(code)
            return {"valid": True}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": str(e),
                "line": e.lineno,
                "offset": e.offset,
                "text": e.text
            }

    def generate_from_prompt(self, prompt: str, asset_category: str = "general") -> Dict[str, Any]:
        """Requests code generation from local Qwen2.5-Coder model or procedural templates."""
        user_message = f"Asset Category: {asset_category}\nRequest: {prompt}\nWrite the complete Blender Python script to construct this asset."
        
        # Check if LM Studio is online
        health = self.lm_client.check_health()
        if health.get("online"):
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT_BPY},
                {"role": "user", "content": user_message}
            ]
            resp = self.lm_client.chat_completion(messages, temperature=0.2, max_tokens=2500)
            if resp.get("status") == "success":
                raw_code = resp.get("content", "")
                code = self.extract_code(raw_code)
                syntax = self.validate_syntax(code)
                return {
                    "status": "success" if syntax["valid"] else "syntax_error",
                    "code": code,
                    "syntax": syntax,
                    "source": "local_qwen_coder"
                }

        # Fallback to intelligent procedural generator library
        code = self._generate_procedural_template(prompt, asset_category)
        syntax = self.validate_syntax(code)
        return {
            "status": "success",
            "code": code,
            "syntax": syntax,
            "source": "procedural_library_engine"
        }

    def _generate_procedural_template(self, prompt: str, category: str) -> str:
        """Provides verified procedural templates for mechanical, architectural, and vehicle assets."""
        prompt_lower = prompt.lower()

        if "gear" in prompt_lower or "mechanical" in prompt_lower or category == "mechanical":
            return """import bpy
import bmesh
import math
import mathutils

# Create procedural mechanical gear / housing
mesh = bpy.data.meshes.new("ProceduralMechanicalAsset")
obj = bpy.data.objects.new("ProceduralMechanicalAsset", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

bm = bmesh.new()

# Parameters
teeth = 16
inner_radius = 0.5
outer_radius = 1.2
tooth_height = 0.3
thickness = 0.4

# Create circular gear vertices
outer_verts = []
for i in range(teeth * 2):
    angle = (2 * math.pi / (teeth * 2)) * i
    r = outer_radius + (tooth_height if i % 2 == 1 else 0.0)
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    outer_verts.append(bm.verts.new((x, y, 0)))

# Create center hole
inner_verts = []
for i in range(teeth * 2):
    angle = (2 * math.pi / (teeth * 2)) * i
    x = inner_radius * math.cos(angle)
    y = inner_radius * math.sin(angle)
    inner_verts.append(bm.verts.new((x, y, 0)))

# Build bottom faces
for i in range(teeth * 2):
    next_i = (i + 1) % (teeth * 2)
    bm.faces.new([inner_verts[i], outer_verts[i], outer_verts[next_i], inner_verts[next_i]])

bm.to_mesh(mesh)
bm.free()

# Extrude via Solidify Modifier
solid = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
solid.thickness = thickness
solid.offset = 1.0

# Add Bevel Modifier for precision mechanical edge highlights
bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.03
bevel.segments = 3

# Apply modifiers
bpy.ops.object.modifier_apply(modifier="Solidify")
bpy.ops.object.modifier_apply(modifier="Bevel")
bpy.ops.object.shade_smooth()

# Create PBR Titanium Material
mat = bpy.data.materials.new(name="PBR_SteelTitanium")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.75, 0.78, 0.82, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.22
obj.data.materials.append(mat)
"""
        elif "hypercar" in prompt_lower or "vehicle" in prompt_lower or category == "vehicle":
            return """import bpy
import math

# Create procedural vehicle body & aerodynamic styling
# Base Aerodynamic Chassis
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0.5))
chassis = bpy.context.active_object
chassis.name = "Hypercar_Chassis"
chassis.scale = (1.1, 2.3, 0.35)
bpy.ops.object.transform_apply(scale=True)

# Cockpit Canopy
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(0, -0.2, 0.75))
canopy = bpy.context.active_object
canopy.name = "Hypercar_Canopy"
canopy.scale = (0.75, 1.4, 0.5)
bpy.ops.object.transform_apply(scale=True)

# Rear Aerodynamic Wing
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.9, 1.0))
wing = bpy.context.active_object
wing.name = "Hypercar_Wing"
wing.scale = (1.9, 0.25, 0.04)
bpy.ops.object.transform_apply(scale=True)

# Wheels
wheel_coords = [(-1.25, 1.3, 0.4), (1.25, 1.3, 0.4), (-1.25, -1.3, 0.4), (1.25, -1.3, 0.4)]
for i, coord in enumerate(wheel_coords):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.35, location=coord, rotation=(0, math.radians(90), 0))
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i+1}"

# Materials: Carbon Metallic Body & Glass
mat_body = bpy.data.materials.new(name="Mat_HypercarBody")
mat_body.use_nodes = True
bsdf = mat_body.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.02, 0.08, 0.2, 1.0) # Deep Racing Blue
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.12
chassis.data.materials.append(mat_body)
wing.data.materials.append(mat_body)
"""
        else:
            return """import bpy

# Generic procedural asset construction
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
obj = bpy.context.active_object
obj.name = "ProceduralAsset"

sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
sub.levels = 2
sub.render_levels = 2

bev = obj.modifiers.new(name="Bevel", type='BEVEL')
bev.width = 0.05
bev.segments = 2

bpy.ops.object.shade_smooth()

mat = bpy.data.materials.new(name="Mat_Procedural")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.2, 0.5, 0.8, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.3
obj.data.materials.append(mat)
"""


if __name__ == "__main__":
    gen = BpyGenerator()
    res = gen.generate_from_prompt("Create a high precision mechanical gear", "mechanical")
    print("Generated code valid:", res["syntax"]["valid"])
    print(res["code"][:300] + "...")

