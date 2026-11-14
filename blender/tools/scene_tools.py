"""Scene inspection and hierarchy querying tools."""

import bpy
from typing import Dict, Any

def inspect_scene(detailed: bool = False, **kwargs) -> Dict[str, Any]:
    """Inspect all objects, active object, collections, and materials in the scene."""
    scene = bpy.context.scene
    objects_info = []

    for obj in scene.objects:
        info = {
            "name": obj.name,
            "type": obj.type,
            "location": [round(v, 4) for v in obj.location],
            "rotation_euler": [round(v, 4) for v in obj.rotation_euler],
            "scale": [round(v, 4) for v in obj.scale],
            "visible": not obj.hide_viewport,
        }
        if detailed and obj.type == 'MESH' and obj.data:
            info["vertices_count"] = len(obj.data.vertices)
            info["polygons_count"] = len(obj.data.polygons)
            info["materials"] = [m.name for m in obj.data.materials if m]
            info["modifiers"] = [mod.name for mod in obj.modifiers]
        objects_info.append(info)

    active_obj = bpy.context.view_layer.objects.active
    return {
        "status": "SUCCESS",
        "scene_name": scene.name,
        "active_object": active_obj.name if active_obj else None,
        "selected_objects": [o.name for o in bpy.context.selected_objects],
        "total_objects": len(scene.objects),
        "objects": objects_info
    }

def inspect_object(object_name: str = "", **kwargs) -> Dict[str, Any]:
    """Detailed inspection of an individual object."""
    if object_name:
        obj = bpy.data.objects.get(object_name)
    else:
        obj = bpy.context.view_layer.objects.active

    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    data = {
        "name": obj.name,
        "type": obj.type,
        "location": [round(v, 4) for v in obj.location],
        "rotation_euler": [round(v, 4) for v in obj.rotation_euler],
        "scale": [round(v, 4) for v in obj.scale],
        "dimensions": [round(v, 4) for v in obj.dimensions],
        "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers]
    }

    if obj.type == 'MESH' and obj.data:
        data["vertices_count"] = len(obj.data.vertices)
        data["edges_count"] = len(obj.data.edges)
        data["polygons_count"] = len(obj.data.polygons)
        data["materials"] = [m.name for m in obj.data.materials if m]
        # Check non-manifold geometry count
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        non_manifold_edges = sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
        data["non_manifold_edges"] = non_manifold_edges

    return {"status": "SUCCESS", "data": data}
