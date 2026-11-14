"""Mesh editing and procedural bmesh operations."""

import bpy
import bmesh
import math
from typing import Dict, Any, List

def create_mesh(name: str, vertices: List[List[float]], faces: List[List[int]], **kwargs) -> Dict[str, Any]:
    """Create a new mesh object directly from vertices and faces."""
    mesh_data = bpy.data.meshes.new(name + "_mesh")
    mesh_data.from_pydata(vertices, [], faces)
    mesh_data.update()

    obj = bpy.data.objects.new(name, mesh_data)
    bpy.context.collection.objects.link(obj)

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    return {
        "status": "SUCCESS",
        "object_name": obj.name,
        "vertices_count": len(vertices),
        "faces_count": len(faces)
    }

def create_truncated_icosahedron(name: str = "Realistic_Football", radius: float = 1.1, **kwargs) -> Dict[str, Any]:
    """Mathematically generate the 60 vertices and 32 panels of a truncated icosahedron."""
    phi = (1.0 + math.sqrt(5.0)) / 2.0

    raw_verts = []
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            raw_verts.append((0.0, s1 * 1.0, s2 * 3.0 * phi))
            raw_verts.append((s1 * 1.0, s2 * 3.0 * phi, 0.0))
            raw_verts.append((s2 * 3.0 * phi, 0.0, s1 * 1.0))

    for s1 in (-1, 1):
        for s2 in (-1, 1):
            for s3 in (-1, 1):
                raw_verts.append((s1 * 2.0, s2 * (1.0 + 2.0 * phi), s3 * phi))
                raw_verts.append((s3 * phi, s1 * 2.0, s2 * (1.0 + 2.0 * phi)))
                raw_verts.append((s2 * (1.0 + 2.0 * phi), s3 * phi, s1 * 2.0))
                raw_verts.append((s1 * 1.0, s2 * (2.0 + phi), s3 * 2.0 * phi))
                raw_verts.append((s3 * 2.0 * phi, s1 * 1.0, s2 * (2.0 + phi)))
                raw_verts.append((s2 * (2.0 + phi), s3 * 2.0 * phi, s1 * 1.0))

    unique_verts = []
    for v in raw_verts:
        if not any(math.isclose(v[0], u[0], abs_tol=1e-4) and
                   math.isclose(v[1], u[1], abs_tol=1e-4) and
                   math.isclose(v[2], u[2], abs_tol=1e-4) for u in unique_verts):
            unique_verts.append(v)

    verts = []
    for x, y, z in unique_verts[:60]:
        dist = math.sqrt(x*x + y*y + z*z)
        verts.append([round((x / dist) * radius, 5), round((y / dist) * radius, 5), round((z / dist) * radius, 5)])

    bm = bmesh.new()
    bm_verts = [bm.verts.new(v) for v in verts]
    bm.verts.ensure_lookup_table()
    bmesh.ops.convex_hull(bm, input=bm_verts)
    faces = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()

    return create_mesh(name=name, vertices=verts, faces=faces)

def edit_mesh(object_name: str, operation: str, distance: float = 0.001, **kwargs) -> Dict[str, Any]:
    """Apply topology cleanup, smoothing, or recalculation on object mesh."""
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {"status": "ERROR", "message": f"Object '{object_name}' is not a valid mesh."}

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    if operation == "recalculate_normals":
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    elif operation == "remove_doubles":
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
    elif operation == "shade_smooth":
        for f in bm.faces:
            f.smooth = True
    elif operation == "beautify_fill":
        bmesh.ops.beautify_fill(bm, faces=bm.faces, method='ANGLE')
    else:
        bm.free()
        return {"status": "ERROR", "message": f"Unsupported mesh operation: {operation}"}

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    return {"status": "SUCCESS", "operation": operation, "object_name": obj.name}

def extrude(object_name: str, offset: float, **kwargs) -> Dict[str, Any]:
    """Extrude faces of an object along face normals."""
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {"status": "ERROR", "message": f"Object '{object_name}' is not a valid mesh."}

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    faces_to_extrude = [f for f in bm.faces]
    res = bmesh.ops.extrude_face_region(bm, geom=faces_to_extrude)
    extruded_verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]

    for f in faces_to_extrude:
        norm = f.normal.copy()
        for v in f.verts:
            if v in extruded_verts:
                v.co += norm * offset

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    return {"status": "SUCCESS", "extruded_offset": offset, "object_name": obj.name}

def inset(object_name: str, thickness: float, depth: float = 0.0, **kwargs) -> Dict[str, Any]:
    """Inset faces of mesh."""
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {"status": "ERROR", "message": f"Object '{object_name}' is not a valid mesh."}

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    bmesh.ops.inset_individual(bm, faces=bm.faces, thickness=thickness, depth=depth)

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    return {"status": "SUCCESS", "thickness": thickness, "depth": depth, "object_name": obj.name}

def bevel(object_name: str, offset: float, segments: int = 2, **kwargs) -> Dict[str, Any]:
    """Directly bevel mesh edges."""
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {"status": "ERROR", "message": f"Object '{object_name}' is not a valid mesh."}

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    bmesh.ops.bevel(bm, geom=bm.edges, offset=offset, segments=segments, affect='EDGES')

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    return {"status": "SUCCESS", "bevel_offset": offset, "segments": segments, "object_name": obj.name}

def subdivide(object_name: str, cuts: int = 1, **kwargs) -> Dict[str, Any]:
    """Subdivide mesh faces."""
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        return {"status": "ERROR", "message": f"Object '{object_name}' is not a valid mesh."}

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=cuts, use_grid_fill=True)

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    return {"status": "SUCCESS", "cuts": cuts, "object_name": obj.name}
