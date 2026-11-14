"""Object manipulation, creation, transformation, and hierarchy tools."""

import bpy
from typing import Dict, Any, List, Optional

def create_object(primitive_type: str, name: str = "", location: Optional[List[float]] = None,
                  rotation: Optional[List[float]] = None, scale: Optional[List[float]] = None,
                  subdivisions: int = 2, **kwargs) -> Dict[str, Any]:
    """Create a 3D primitive on the main thread."""
    loc = tuple(location) if location else (0.0, 0.0, 0.0)
    rot = tuple(rotation) if rotation else (0.0, 0.0, 0.0)
    sc = tuple(scale) if scale else (1.0, 1.0, 1.0)

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    pt = primitive_type.lower()
    if pt == "cube":
        bpy.ops.mesh.primitive_cube_add(size=2.0, location=loc, rotation=rot, scale=sc)
    elif pt == "uv_sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=loc, rotation=rot, scale=sc, segments=max(8, subdivisions * 16), ring_count=max(8, subdivisions * 8))
    elif pt == "ico_sphere":
        bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=subdivisions, location=loc, rotation=rot, scale=sc)
    elif pt == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=2.0, location=loc, rotation=rot, scale=sc)
    elif pt == "cone":
        bpy.ops.mesh.primitive_cone_add(radius1=1.0, depth=2.0, location=loc, rotation=rot, scale=sc)
    elif pt == "torus":
        bpy.ops.mesh.primitive_torus_add(location=loc, rotation=rot)
    elif pt == "plane":
        bpy.ops.mesh.primitive_plane_add(size=2.0, location=loc, rotation=rot, scale=sc)
    else:
        return {"status": "ERROR", "message": f"Unsupported primitive type: '{primitive_type}'"}

    obj = bpy.context.active_object
    if name and obj:
        obj.name = name

    return {
        "status": "SUCCESS",
        "object_name": obj.name,
        "location": list(obj.location),
        "type": obj.type
    }

def delete_object(object_name: str, confirm: bool = False, **kwargs) -> Dict[str, Any]:
    """Delete an object from the scene with confirmation guard."""
    if not confirm:
        return {"status": "ERROR", "message": "Deletion aborted: confirm=True required."}

    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    # Unlink mesh data if no other users
    mesh_data = obj.data if obj.type == 'MESH' else None
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh_data and mesh_data.users == 0:
        bpy.data.meshes.remove(mesh_data)

    return {"status": "SUCCESS", "deleted": object_name}

def select_object(object_name: str, **kwargs) -> Dict[str, Any]:
    """Select an object and make it active."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return {"status": "SUCCESS", "active_object": obj.name}

def transform_object(object_name: str, location: Optional[List[float]] = None,
                     rotation: Optional[List[float]] = None, scale: Optional[List[float]] = None, **kwargs) -> Dict[str, Any]:
    """Apply transformation to an object."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    if location is not None:
        obj.location = tuple(location)
    if rotation is not None:
        obj.rotation_euler = tuple(rotation)
    if scale is not None:
        obj.scale = tuple(scale)

    return {
        "status": "SUCCESS",
        "object_name": obj.name,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale)
    }

def duplicate_object(source_name: str, new_name: str = "", location_offset: Optional[List[float]] = None, **kwargs) -> Dict[str, Any]:
    """Duplicate an existing object with optional offset."""
    src = bpy.data.objects.get(source_name)
    if not src:
        return {"status": "ERROR", "message": f"Source object '{source_name}' not found."}

    new_obj = src.copy()
    if src.data:
        new_obj.data = src.data.copy()

    if new_name:
        new_obj.name = new_name

    if location_offset:
        new_obj.location.x += location_offset[0]
        new_obj.location.y += location_offset[1]
        new_obj.location.z += location_offset[2]

    bpy.context.collection.objects.link(new_obj)
    bpy.ops.object.select_all(action='DESELECT')
    new_obj.select_set(True)
    bpy.context.view_layer.objects.active = new_obj

    return {"status": "SUCCESS", "duplicate_name": new_obj.name}
