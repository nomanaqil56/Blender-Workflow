"""
Test football geometry generation script to verify manifold topology,
exact spherical dimensions, and panel layout.
"""

import bpy
import bmesh
import mathutils
import json

bpy.ops.wm.read_factory_settings(use_empty=True)

# Step 1: Base Icosahedron at origin (0, 0, 0)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "Football"

# Step 2: BMesh truncation (12 pentagons, 20 hexagons)
bm = bmesh.new()
bm.from_mesh(ball.data)

# Bevel vertices by 1/3
bmesh.ops.bevel(
    bm,
    geom=bm.verts[:],
    offset=0.33333333,
    offset_type='OFFSET',
    affect='VERTICES',
    segments=1
)

# Normalize all 60 vertices to exact sphere radius
for v in bm.verts:
    v.co = v.co.normalized() * 1.0

# Count pentagons & hexagons
pents = [f for f in bm.faces if len(f.verts) == 5]
hexes = [f for f in bm.faces if len(f.verts) == 6]

print(f"Truncated Icosahedron: {len(pents)} pentagons, {len(hexes)} hexagons")
assert len(pents) == 12, f"Expected 12 pentagons, got {len(pents)}"
assert len(hexes) == 20, f"Expected 20 hexagons, got {len(hexes)}"

# Materials slots
mat_white = bpy.data.materials.new("White")
mat_black = bpy.data.materials.new("Black")
mat_seam = bpy.data.materials.new("Seam")
ball.data.materials.append(mat_white) # 0
ball.data.materials.append(mat_black) # 1
ball.data.materials.append(mat_seam)  # 2

for f in pents:
    f.material_index = 1
for f in hexes:
    f.material_index = 0

# Inset panels to create seams
all_panels = bm.faces[:]
res_inset = bmesh.ops.inset_individual(
    bm,
    faces=all_panels,
    thickness=0.015,
    depth=0.0,
    use_even_offset=True
)

inner_faces = set(res_inset['faces'])
side_quads = [f for f in bm.faces if f not in inner_faces]

# Assign seam material to side quads
for f in side_quads:
    f.material_index = 2

# Push inner panel faces slightly outward along their normals for leather inflation
for f in inner_faces:
    normal = f.normal.copy()
    for v in f.verts:
        v.co += normal * 0.012

# Check non-manifold geometry before exiting
non_manifold_verts = [v for v in bm.verts if not v.is_manifold]
non_manifold_edges = [e for e in bm.edges if not e.is_manifold]

print(f"Non-manifold vertices: {len(non_manifold_verts)}, Non-manifold edges: {len(non_manifold_edges)}")

bm.to_mesh(ball.data)
bm.free()

ball.location = (0, 0, 1.02)
bpy.context.view_layer.update()

dim = list(ball.dimensions)
print("Ball dimensions:", dim)

is_spherical = abs(dim[0] - dim[1]) < 0.05 and abs(dim[1] - dim[2]) < 0.05
print("Is spherical:", is_spherical)
print("Is 100% manifold:", len(non_manifold_edges) == 0)

with open(r"D:\AI Local\Blender AI Studio\Reports\football_geom_check.json", "w") as f:
    json.dump({
        "pentagons": len(pents),
        "hexagons": len(hexes),
        "total_faces": len(ball.data.polygons),
        "dimensions": dim,
        "is_spherical": is_spherical,
        "non_manifold_vertices": len(non_manifold_verts),
        "non_manifold_edges": len(non_manifold_edges),
        "is_manifold": (len(non_manifold_edges) == 0)
    }, f, indent=2)
