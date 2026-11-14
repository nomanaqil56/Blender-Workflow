"""Central Tool Registry defining tool schemas for LLM tool calling."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ToolDefinition:
    name: str
    description: str
    category: str
    parameters_schema: Dict[str, Any]
    is_destructive: bool = False

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> Optional[ToolDefinition]:
        return self._tools.get(tool_name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def get_openai_tools_schema(self) -> List[Dict[str, Any]]:
        """Return schema suitable for OpenAI / LM Studio function calling."""
        schema = []
        for t in self._tools.values():
            schema.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters_schema
                }
            })
        return schema

    def _register_default_tools(self):
        # 1. Scene Tools
        self.register(ToolDefinition(
            name="inspect_scene",
            description="Inspect objects, collections, materials, and active state in the current Blender scene.",
            category="scene",
            parameters_schema={
                "type": "object",
                "properties": {
                    "detailed": {"type": "boolean", "description": "Include detailed vertex/face counts and bounding boxes", "default": False}
                }
            }
        ))
        self.register(ToolDefinition(
            name="inspect_object",
            description="Inspect a specific object's transforms, mesh statistics, materials, and modifier stack.",
            category="scene",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of object to inspect. If omitted, uses active object."}
                }
            }
        ))

        # 2. Object Tools
        self.register(ToolDefinition(
            name="create_object",
            description="Create a standard 3D primitive (cube, uv_sphere, ico_sphere, cylinder, cone, torus, plane).",
            category="object",
            parameters_schema={
                "type": "object",
                "properties": {
                    "primitive_type": {"type": "string", "enum": ["cube", "uv_sphere", "ico_sphere", "cylinder", "cone", "torus", "plane"], "description": "Primitive shape"},
                    "name": {"type": "string", "description": "Name for the created object"},
                    "location": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] coordinate"},
                    "rotation": {"type": "array", "items": {"type": "number"}, "description": "[rx, ry, rz] in radians"},
                    "scale": {"type": "array", "items": {"type": "number"}, "description": "[sx, sy, sz] scale factor"},
                    "subdivisions": {"type": "integer", "description": "Subdivisions for ico_sphere or uv_sphere segments"}
                },
                "required": ["primitive_type"]
            }
        ))
        self.register(ToolDefinition(
            name="delete_object",
            description="Delete an object from the scene (requires confirm=True).",
            category="object",
            is_destructive=True,
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of object to delete"},
                    "confirm": {"type": "boolean", "description": "Explicit confirmation flag", "default": False}
                },
                "required": ["object_name", "confirm"]
            }
        ))
        self.register(ToolDefinition(
            name="select_object",
            description="Set the active and selected object in Blender.",
            category="object",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of object to select"}
                },
                "required": ["object_name"]
            }
        ))
        self.register(ToolDefinition(
            name="transform_object",
            description="Translate, rotate, or scale an object.",
            category="object",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of object"},
                    "location": {"type": "array", "items": {"type": "number"}},
                    "rotation": {"type": "array", "items": {"type": "number"}},
                    "scale": {"type": "array", "items": {"type": "number"}}
                },
                "required": ["object_name"]
            }
        ))
        self.register(ToolDefinition(
            name="duplicate_object",
            description="Duplicate an existing object with optional transformation.",
            category="object",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_name": {"type": "string", "description": "Name of object to duplicate"},
                    "new_name": {"type": "string", "description": "Name for duplicate"},
                    "location_offset": {"type": "array", "items": {"type": "number"}}
                },
                "required": ["source_name"]
            }
        ))

        # 3. Mesh Operations
        self.register(ToolDefinition(
            name="create_truncated_icosahedron",
            description="Create mathematically exact truncated icosahedron mesh (12 pentagons and 20 hexagons) for soccer ball panels.",
            category="mesh",
            parameters_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "default": "Realistic_Football"},
                    "radius": {"type": "number", "default": 1.1}
                }
            }
        ))
        self.register(ToolDefinition(
            name="create_mesh",
            description="Create custom geometry from vertices and face indices.",
            category="mesh",
            parameters_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Mesh name"},
                    "vertices": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                    "faces": {"type": "array", "items": {"type": "array", "items": {"type": "integer"}}}
                },
                "required": ["name", "vertices", "faces"]
            }
        ))
        self.register(ToolDefinition(
            name="edit_mesh",
            description="Perform bmesh operations like smooth normals, recalculate normals, dissolve degenerate, remove doubles.",
            category="mesh",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "operation": {"type": "string", "enum": ["recalculate_normals", "shade_smooth", "remove_doubles", "beautify_fill"]},
                    "distance": {"type": "number", "description": "Merge distance for remove_doubles", "default": 0.001}
                },
                "required": ["object_name", "operation"]
            }
        ))
        self.register(ToolDefinition(
            name="extrude",
            description="Extrude selected faces or all boundary faces along normals.",
            category="mesh",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "offset": {"type": "number", "description": "Extrusion distance"}
                },
                "required": ["object_name", "offset"]
            }
        ))
        self.register(ToolDefinition(
            name="inset",
            description="Inset faces on the active mesh.",
            category="mesh",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "thickness": {"type": "number", "description": "Inset thickness distance"},
                    "depth": {"type": "number", "description": "Depth offset", "default": 0.0}
                },
                "required": ["object_name", "thickness"]
            }
        ))
        self.register(ToolDefinition(
            name="bevel",
            description="Bevel edges of the mesh geometry directly.",
            category="mesh",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "offset": {"type": "number", "description": "Bevel width offset"},
                    "segments": {"type": "integer", "description": "Number of bevel segments", "default": 2}
                },
                "required": ["object_name", "offset"]
            }
        ))
        self.register(ToolDefinition(
            name="subdivide",
            description="Subdivide mesh faces.",
            category="mesh",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "cuts": {"type": "integer", "description": "Number of cuts", "default": 1}
                },
                "required": ["object_name"]
            }
        ))

        # 4. Modifiers
        self.register(ToolDefinition(
            name="add_modifier",
            description="Add a modifier (SUBSURF, BEVEL, SOLIDIFY, BOOLEAN, MIRROR, REMESH, ARRAY).",
            category="modifier",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "modifier_type": {"type": "string", "enum": ["SUBSURF", "BEVEL", "SOLIDIFY", "BOOLEAN", "MIRROR", "REMESH", "ARRAY", "CAST"]},
                    "modifier_name": {"type": "string"},
                    "properties": {"type": "object", "description": "Modifier properties dictionary"}
                },
                "required": ["object_name", "modifier_type"]
            }
        ))
        self.register(ToolDefinition(
            name="configure_modifier",
            description="Update properties on an existing modifier.",
            category="modifier",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "modifier_name": {"type": "string"},
                    "properties": {"type": "object"}
                },
                "required": ["object_name", "modifier_name", "properties"]
            }
        ))
        self.register(ToolDefinition(
            name="apply_modifier",
            description="Apply a modifier to permanently bake its effect into geometry.",
            category="modifier",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "modifier_name": {"type": "string"}
                },
                "required": ["object_name", "modifier_name"]
            }
        ))

        # 5. Materials
        self.register(ToolDefinition(
            name="create_material",
            description="Create a PBR material with Principled BSDF shader properties (color, metallic, roughness, etc.).",
            category="material",
            parameters_schema={
                "type": "object",
                "properties": {
                    "material_name": {"type": "string"},
                    "base_color": {"type": "array", "items": {"type": "number"}, "description": "[R, G, B, A]"},
                    "metallic": {"type": "number", "default": 0.0},
                    "roughness": {"type": "number", "default": 0.4},
                    "specular": {"type": "number", "default": 0.5},
                    "transmission": {"type": "number", "default": 0.0},
                    "emission_color": {"type": "array", "items": {"type": "number"}},
                    "emission_strength": {"type": "number", "default": 0.0}
                },
                "required": ["material_name"]
            }
        ))
        self.register(ToolDefinition(
            name="assign_material",
            description="Assign an existing material to an object or specific face index range.",
            category="material",
            parameters_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "material_name": {"type": "string"},
                    "slot_index": {"type": "integer", "default": 0}
                },
                "required": ["object_name", "material_name"]
            }
        ))

        # 6. Lighting & Cameras
        self.register(ToolDefinition(
            name="setup_camera",
            description="Create or configure a camera, positioning and framing target object.",
            category="camera",
            parameters_schema={
                "type": "object",
                "properties": {
                    "camera_name": {"type": "string", "default": "Studio_Camera"},
                    "location": {"type": "array", "items": {"type": "number"}},
                    "rotation": {"type": "array", "items": {"type": "number"}},
                    "target_object": {"type": "string", "description": "Track camera to target object"},
                    "focal_length": {"type": "number", "default": 50.0},
                    "set_as_active": {"type": "boolean", "default": True}
                }
            }
        ))
        self.register(ToolDefinition(
            name="setup_light",
            description="Add or adjust studio lights (SUN, POINT, SPOT, AREA) with energy and color.",
            category="lighting",
            parameters_schema={
                "type": "object",
                "properties": {
                    "light_name": {"type": "string"},
                    "light_type": {"type": "string", "enum": ["POINT", "SUN", "SPOT", "AREA"], "default": "AREA"},
                    "energy": {"type": "number", "default": 500.0},
                    "color": {"type": "array", "items": {"type": "number"}, "description": "[R, G, B]"},
                    "location": {"type": "array", "items": {"type": "number"}},
                    "rotation": {"type": "array", "items": {"type": "number"}},
                    "size": {"type": "number", "default": 2.0}
                },
                "required": ["light_name"]
            }
        ))

        # 7. Render & Viewport
        self.register(ToolDefinition(
            name="render_preview",
            description="Render the active scene to an image file with Cycles OptiX or EEVEE.",
            category="render",
            parameters_schema={
                "type": "object",
                "properties": {
                    "output_filename": {"type": "string"},
                    "samples": {"type": "integer", "default": 64},
                    "resolution": {"type": "array", "items": {"type": "integer"}, "default": [1280, 720]},
                    "engine": {"type": "string", "enum": ["CYCLES", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"], "default": "CYCLES"}
                }
            }
        ))
        self.register(ToolDefinition(
            name="capture_viewport",
            description="Capture current 3D viewport screenshot immediately.",
            category="render",
            parameters_schema={
                "type": "object",
                "properties": {
                    "output_filename": {"type": "string", "default": "viewport_capture.png"}
                }
            }
        ))

        # 8. File Operations
        self.register(ToolDefinition(
            name="save_project",
            description="Save the current Blender scene to a .blend file.",
            category="file",
            parameters_schema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Filename or path to save"}
                }
            }
        ))
        self.register(ToolDefinition(
            name="export_asset",
            description="Export the scene or selected objects to GLB, OBJ, or FBX.",
            category="file",
            parameters_schema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Target export path"},
                    "format": {"type": "string", "enum": ["glb", "obj", "fbx"], "default": "glb"},
                    "selected_only": {"type": "boolean", "default": False}
                },
                "required": ["filepath"]
            }
        ))

tool_registry = ToolRegistry()
