"""UV unwrapping and projection tools."""

import bpy
from typing import Dict, Any

def uv_unwrap(object_name: str, method: str = "smart_project", island_margin: float = 0.02, **kwargs) -> Dict[str, Any]:
    """Perform automated UV unwrapping."""
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {"status": "ERROR", "message": f"Object '{object_name}' is not a valid mesh."}

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    if method == "smart_project":
        bpy.ops.uv.smart_project(island_margin=island_margin)
    elif method == "cube_project":
        bpy.ops.uv.cube_project()
    elif method == "sphere_project":
        bpy.ops.uv.sphere_project()
    else:
        bpy.ops.uv.unwrap()

    bpy.ops.object.mode_set(mode='OBJECT')

    return {"status": "SUCCESS", "object_name": obj.name, "method": method}
