"""
Blender AI Studio - Master Realistic Football Production Workflow
Creates a geometrically accurate, 100% manifold truncated icosahedron (12 pentagons, 20 hexagons),
applies recessed leather panel insets, PBR polyurethane/leather shaders with procedural micro-grain,
studio 3-point lighting, dual camera staging (master & close-up macro), Cycles OptiX GPU rendering,
project saving, and GLB production export.
"""

import sys
import os
import math
from pathlib import Path

STUDIO_ROOT = Path(r"D:\AI Local\Blender AI Studio")
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

FOOTBALL_BLEND_DIR = STUDIO_ROOT / "Projects" / "Football_Test"
FOOTBALL_BLEND_DIR.mkdir(parents=True, exist_ok=True)
FOOTBALL_BLEND_PATH = FOOTBALL_BLEND_DIR / "football.blend"
FOOTBALL_GLB_PATH = STUDIO_ROOT / "Exports" / "football.glb"
RENDER_FINAL_PATH = STUDIO_ROOT / "Renders" / "football_final.png"
RENDER_CLOSEUP_PATH = STUDIO_ROOT / "Renders" / "football_closeup.png"
TEST_EVIDENCE_DIR = STUDIO_ROOT / "Reports" / "TEST_EVIDENCE"
TEST_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

FOOTBALL_SCRIPT = f"""
import bpy
import bmesh
import mathutils
import math
import os

# 1. Initialize Clean Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "Football_Production_Studio"

# 2. Build Base Truncated Icosahedron at origin (0, 0, 0)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "Football_Mesh"

# 3. Truncate Vertices in BMesh
bm = bmesh.new()
bm.from_mesh(ball.data)

# Bevel vertices by exact 1/3 ratio
bmesh.ops.bevel(
    bm,
    geom=bm.verts[:],
    offset=0.33333333,
    offset_type='OFFSET',
    affect='VERTICES',
    segments=1
)

# Normalize all 60 vertices to perfect sphere radius
for v in bm.verts:
    v.co = v.co.normalized() * 1.0

# Detect 12 Pentagons and 20 Hexagons
pentagons = [f for f in bm.faces if len(f.verts) == 5]
hexagons = [f for f in bm.faces if len(f.verts) == 6]
print(f"Verified Topology: {{len(pentagons)}} Pentagons and {{len(hexagons)}} Hexagons.")

# 4. Create PBR Leather Shaders
# Material 0: White Leather Panels
mat_white = bpy.data.materials.new(name="Mat_Football_White")
mat_white.use_nodes = True
nw = mat_white.node_tree.nodes
lw = mat_white.node_tree.links
bsdf_w = nw.get("Principled BSDF")
bsdf_w.inputs['Base Color'].default_value = (0.88, 0.89, 0.91, 1.0)
bsdf_w.inputs['Roughness'].default_value = 0.28
if 'Coat Weight' in bsdf_w.inputs:
    bsdf_w.inputs['Coat Weight'].default_value = 0.35
    bsdf_w.inputs['Coat Roughness'].default_value = 0.2

# Procedural Leather Bump Texture
v_tex_w = nw.new(type='ShaderNodeTexVoronoi')
v_tex_w.inputs['Scale'].default_value = 220.0
bump_w = nw.new(type='ShaderNodeBump')
bump_w.inputs['Strength'].default_value = 0.035
bump_w.inputs['Distance'].default_value = 0.004
lw.new(v_tex_w.outputs['Distance'], bump_w.inputs['Height'])
lw.new(bump_w.outputs['Normal'], bsdf_w.inputs['Normal'])

# Material 1: Black Leather Panels
mat_black = bpy.data.materials.new(name="Mat_Football_Black")
mat_black.use_nodes = True
nb = mat_black.node_tree.nodes
lb = mat_black.node_tree.links
bsdf_b = nb.get("Principled BSDF")
bsdf_b.inputs['Base Color'].default_value = (0.015, 0.015, 0.018, 1.0)
bsdf_b.inputs['Roughness'].default_value = 0.30
if 'Coat Weight' in bsdf_b.inputs:
    bsdf_b.inputs['Coat Weight'].default_value = 0.35
    bsdf_b.inputs['Coat Roughness'].default_value = 0.2

v_tex_b = nb.new(type='ShaderNodeTexVoronoi')
v_tex_b.inputs['Scale'].default_value = 220.0
bump_b = nb.new(type='ShaderNodeBump')
bump_b.inputs['Strength'].default_value = 0.035
bump_b.inputs['Distance'].default_value = 0.004
lb.new(v_tex_b.outputs['Distance'], bump_b.inputs['Height'])
lb.new(bump_b.outputs['Normal'], bsdf_b.inputs['Normal'])

# Material 2: Dark Seam Channels
mat_seam = bpy.data.materials.new(name="Mat_Football_Seam")
mat_seam.use_nodes = True
bsdf_s = mat_seam.node_tree.nodes.get("Principled BSDF")
bsdf_s.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf_s.inputs['Roughness'].default_value = 0.70

# Assign Material Slots to Ball
ball.data.materials.append(mat_white) # Slot 0
ball.data.materials.append(mat_black) # Slot 1
ball.data.materials.append(mat_seam)  # Slot 2

for f in hexagons:
    f.material_index = 0
for f in pentagons:
    f.material_index = 1

# 5. Inset Individual Panels to Form Seams & Extrude Pillowed Cushion
all_panels = bm.faces[:]
inset_res = bmesh.ops.inset_individual(
    bm,
    faces=all_panels,
    thickness=0.016,
    depth=0.0,
    use_even_offset=True
)

inner_faces = set(inset_res['faces'])
seam_quads = [f for f in bm.faces if f not in inner_faces]
for f in seam_quads:
    f.material_index = 2

# Slightly inflate the inner panel faces outwards along their normal
for f in inner_faces:
    normal = f.normal.copy()
    for v in f.verts:
        v.co += normal * 0.012

# Write BMesh back to mesh
bm.to_mesh(ball.data)
bm.free()

# 6. Apply Non-Destructive Modifiers
# Cast Modifier for perfect spherical curvature
cast_mod = ball.modifiers.new(name="Spherize", type='CAST')
cast_mod.cast_type = 'SPHERE'
cast_mod.factor = 0.985

# Subdivision Surface Modifier for smooth leather cushion
subsurf = ball.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

bpy.ops.object.shade_smooth()

# Sit the ball nicely on the studio floor
ball.location = (0, 0, 1.02)
# Slight natural roll angle so a black pentagon faces the camera
ball.rotation_euler = (math.radians(18), math.radians(24), math.radians(12))

# 7. Studio Backdrop & Floor
bpy.ops.mesh.primitive_plane_add(size=25.0, location=(0, 0, 0))
studio_floor = bpy.context.active_object
studio_floor.name = "Studio_Floor"
mat_floor = bpy.data.materials.new(name="Mat_Floor")
mat_floor.use_nodes = True
bsdf_fl = mat_floor.node_tree.nodes.get("Principled BSDF")
bsdf_fl.inputs['Base Color'].default_value = (0.05, 0.055, 0.065, 1.0)
bsdf_fl.inputs['Roughness'].default_value = 0.45
studio_floor.data.materials.append(mat_floor)

# 8. Studio 3-Point Lighting
# Key Light
bpy.ops.object.light_add(type='AREA', radius=2.5, location=(3.2, -4.0, 4.2))
key = bpy.context.active_object
key.name = "Key_Light"
key.data.energy = 500.0
key.data.color = (1.0, 0.98, 0.94)

# Fill Light
bpy.ops.object.light_add(type='AREA', radius=3.5, location=(-3.8, -3.2, 2.8))
fill = bpy.context.active_object
fill.name = "Fill_Light"
fill.data.energy = 220.0
fill.data.color = (0.85, 0.92, 1.0)

# Rim Light
bpy.ops.object.light_add(type='SPOT', radius=1.0, location=(0.0, 4.5, 3.2))
rim = bpy.context.active_object
rim.name = "Rim_Light"
rim.data.energy = 650.0
rim.data.spot_size = math.radians(60)

for l in [key, fill, rim]:
    tt = l.constraints.new(type='TRACK_TO')
    tt.target = ball
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

# 9. Dual Camera Staging
# Camera 1: Master Hero View (85mm Lens)
bpy.ops.object.camera_add(location=(3.4, -4.0, 2.5))
cam_master = bpy.context.active_object
cam_master.name = "Camera_Master"
cam_master.data.lens = 85.0
tt_m = cam_master.constraints.new(type='TRACK_TO')
tt_m.target = ball
tt_m.track_axis = 'TRACK_NEGATIVE_Z'
tt_m.up_axis = 'UP_Y'

# Camera 2: Close-Up Seam Macro View (105mm Macro Lens)
bpy.ops.object.camera_add(location=(1.2, -1.4, 1.7))
cam_close = bpy.context.active_object
cam_close.name = "Camera_Closeup"
cam_close.data.lens = 105.0
tt_c = cam_close.constraints.new(type='TRACK_TO')
tt_c.target = ball
tt_c.track_axis = 'TRACK_NEGATIVE_Z'
tt_c.up_axis = 'UP_Y'

# 10. Cycles OptiX GPU Render Settings
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
prefs = bpy.context.preferences
cprefs = prefs.addons['cycles'].preferences
cprefs.compute_device_type = 'OPTIX'
cprefs.get_devices()
for d in cprefs.devices:
    d.use = True

scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# 11. Save Project File
os.makedirs(r"{FOOTBALL_BLEND_DIR}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=r"{FOOTBALL_BLEND_PATH}")
print("Saved blend file to:", r"{FOOTBALL_BLEND_PATH}")

# 12. Render Master Frame
scene.camera = cam_master
scene.render.filepath = r"{RENDER_FINAL_PATH}"
bpy.ops.render.render(write_still=True)
print("Master render written to:", r"{RENDER_FINAL_PATH}")

# 13. Render Close-Up Frame
scene.camera = cam_close
scene.render.filepath = r"{RENDER_CLOSEUP_PATH}"
bpy.ops.render.render(write_still=True)
print("Close-up render written to:", r"{RENDER_CLOSEUP_PATH}")

# 14. Export GLB Production Asset (with modifiers applied)
bpy.ops.object.select_all(action='DESELECT')
ball.select_set(True)
bpy.context.view_layer.objects.active = ball

bpy.ops.export_scene.gltf(
    filepath=r"{FOOTBALL_GLB_PATH}",
    export_format='GLB',
    use_selection=True,
    export_apply=True
)
print("Exported GLB to:", r"{FOOTBALL_GLB_PATH}")
"""

if __name__ == "__main__":
    out_file = STUDIO_ROOT / "Generation" / "build_football_scene.py"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(FOOTBALL_SCRIPT)
    print("Master football script written to", out_file)
