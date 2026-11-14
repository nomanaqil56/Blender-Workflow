#!/usr/bin/env python3
"""
Blender AI Studio - Model Context Protocol (MCP) Server
Standard STDIO JSON-RPC 2.0 implementation providing native tool calling
for Antigravity to interact directly with Blender 5.3.
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(r"D:\AI Local\Blender AI Studio")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Core.blender_bridge import BlenderBridge

bridge = BlenderBridge()

TOOLS = [
    {
        "name": "blender_inspect_scene",
        "description": "Inspects all objects, materials, cameras, lights, and render settings in the active Blender scene.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "blender_create_object",
        "description": "Creates a primitive 3D mesh (cube, sphere, cylinder, cone, plane, torus, monkey) or empty object.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "obj_type": {"type": "string", "enum": ["cube", "sphere", "cylinder", "cone", "plane", "torus", "monkey", "empty"], "description": "Type of object to create."},
                "name": {"type": "string", "description": "Unique name for the object."},
                "location": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] coordinates."},
                "rotation": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] rotation in degrees."},
                "scale": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] scaling."},
                "size": {"type": "number", "description": "Base size/radius of the primitive."}
            },
            "required": ["obj_type"]
        }
    },
    {
        "name": "blender_modify_object",
        "description": "Modifies transforms, visibility, or applies transform matrices of an object in Blender.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of object to modify."},
                "location": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] translation."},
                "rotation": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] rotation in degrees."},
                "scale": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] scaling."},
                "visible": {"type": "boolean", "description": "Visibility flag."},
                "select": {"type": "boolean", "description": "Select and make active."},
                "apply_transforms": {"type": "boolean", "description": "Apply location/rotation/scale transforms to mesh data."}
            },
            "required": ["name"]
        }
    },
    {
        "name": "blender_mesh_operations",
        "description": "Performs geometric operations: subdivide, recalculate_normals, merge_by_distance, shade_smooth, shade_flat, remesh, boolean, decimate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of mesh object."},
                "action": {"type": "string", "enum": ["subdivide", "recalculate_normals", "merge_by_distance", "shade_smooth", "shade_flat", "remesh", "boolean", "decimate"]},
                "params": {"type": "object", "description": "Operation specific parameters (e.g. cuts, voxel_size, target, operation)."}
            },
            "required": ["name", "action"]
        }
    },
    {
        "name": "blender_create_material",
        "description": "Creates a Principled BSDF PBR material and optionally assigns it to an object.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Material name."},
                "pbr_properties": {
                    "type": "object",
                    "properties": {
                        "base_color": {"type": "array", "items": {"type": "number"}, "description": "RGB or RGBA [0.0 - 1.0]"},
                        "metallic": {"type": "number", "description": "Metallic factor [0.0 - 1.0]"},
                        "roughness": {"type": "number", "description": "Roughness factor [0.0 - 1.0]"},
                        "ior": {"type": "number", "description": "Index of refraction"},
                        "emission_color": {"type": "array", "items": {"type": "number"}},
                        "emission_strength": {"type": "number"}
                    }
                },
                "assign_to": {"type": "string", "description": "Object name to assign the material to."}
            },
            "required": ["name"]
        }
    },
    {
        "name": "blender_assign_texture",
        "description": "Loads an image and connects it to a material node (diffuse, normal, roughness, metallic).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "material_name": {"type": "string", "description": "Name of target material."},
                "texture_type": {"type": "string", "enum": ["diffuse", "normal", "roughness", "metallic"]},
                "image_path": {"type": "string", "description": "Absolute path to texture image file."}
            },
            "required": ["material_name", "texture_type", "image_path"]
        }
    },
    {
        "name": "blender_setup_lighting",
        "description": "Creates or adjusts a light source in the scene (SUN, POINT, SPOT, AREA).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Light object name."},
                "light_type": {"type": "string", "enum": ["SUN", "POINT", "SPOT", "AREA"]},
                "energy": {"type": "number", "description": "Luminous power/energy."},
                "color": {"type": "array", "items": {"type": "number"}, "description": "RGB color vector."},
                "location": {"type": "array", "items": {"type": "number"}},
                "rotation": {"type": "array", "items": {"type": "number"}}
            }
        }
    },
    {
        "name": "blender_setup_camera",
        "description": "Positions and configures scene camera with optional look-at coordinate tracking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Camera object name."},
                "location": {"type": "array", "items": {"type": "number"}},
                "rotation": {"type": "array", "items": {"type": "number"}},
                "focal_length": {"type": "number", "description": "Focal length in mm (e.g. 50.0)."},
                "look_at": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] target position to track."}
            }
        }
    },
    {
        "name": "blender_geometry_nodes",
        "description": "Applies procedural Geometry Nodes modifier (subdivision, wireframe, procedural displace).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "Target mesh object name."},
                "node_graph_type": {"type": "string", "enum": ["subdivision", "wireframe", "mesh_to_curve"]},
                "params": {"type": "object", "description": "Graph parameters (e.g. radius, level)."}
            },
            "required": ["object_name", "node_graph_type"]
        }
    },
    {
        "name": "blender_render",
        "description": "Renders scene to disk using Cycles (OptiX GPU accelerated) or EEVEE Next.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Output PNG image path."},
                "engine": {"type": "string", "enum": ["CYCLES", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"]},
                "resolution_x": {"type": "integer", "description": "Horizontal resolution in pixels."},
                "resolution_y": {"type": "integer", "description": "Vertical resolution in pixels."},
                "samples": {"type": "integer", "description": "Render samples count."},
                "device": {"type": "string", "enum": ["GPU", "CPU"]}
            },
            "required": ["output_path"]
        }
    },
    {
        "name": "blender_inspect_render",
        "description": "Validates render image resolution, file size, and existence on disk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "Path to rendered image file."}
            },
            "required": ["image_path"]
        }
    },
    {
        "name": "blender_save_project",
        "description": "Saves current Blender production scene to a .blend file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Destination .blend file path."}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "blender_import_asset",
        "description": "Imports 3D asset file (GLB, OBJ, FBX, STL, PLY) into active Blender scene.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to 3D asset file."},
                "format": {"type": "string", "enum": ["glb", "gltf", "obj", "fbx", "stl", "ply"]}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "blender_export_asset",
        "description": "Exports scene or selected objects to production 3D asset (GLB, OBJ, FBX, STL, USDC).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Destination export file path."},
                "format": {"type": "string", "enum": ["glb", "gltf", "obj", "fbx", "stl", "usdc"]},
                "selected_only": {"type": "boolean", "description": "Export selected objects only."}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "blender_execute_script",
        "description": "Executes arbitrary procedural Python bpy code with execution logging.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code targeting bpy."}
            },
            "required": ["code"]
        }
    }
]


def handle_tool_call(name: str, args: dict) -> dict:
    """Dispatches MCP tool call to BlenderBridge."""
    fn_map = {
        "blender_inspect_scene": lambda: bridge.inspect_scene(),
        "blender_create_object": lambda: bridge.create_object(**args),
        "blender_modify_object": lambda: bridge.modify_object(**args),
        "blender_mesh_operations": lambda: bridge.mesh_operations(**args),
        "blender_create_material": lambda: bridge.create_material(**args),
        "blender_assign_texture": lambda: bridge.assign_texture(**args),
        "blender_setup_lighting": lambda: bridge.setup_lighting(**args),
        "blender_setup_camera": lambda: bridge.setup_camera(**args),
        "blender_geometry_nodes": lambda: bridge.apply_geometry_nodes(**args),
        "blender_render": lambda: bridge.render(**args),
        "blender_inspect_render": lambda: bridge.inspect_render(**args),
        "blender_save_project": lambda: bridge.save_project(**args),
        "blender_import_asset": lambda: bridge.import_asset(**args),
        "blender_export_asset": lambda: bridge.export_asset(**args),
        "blender_execute_script": lambda: bridge.execute_script(**args),
    }

    if name not in fn_map:
        return {"error": f"Tool '{name}' not found."}

    try:
        res = fn_map[name]()
        return res
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}


def main():
    """Main JSON-RPC stdio event loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "blender-ai-studio",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            call_res = handle_tool_call(tool_name, tool_args)
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(call_res, indent=2)
                        }
                    ],
                    "isError": call_res.get("status") == "error" or "error" in call_res
                }
            }
        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
        else:
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            }

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

