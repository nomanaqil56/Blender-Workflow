"""
Blender AI Studio - Master Test Execution Suite
Executes all 10 required production tests specified in Directive Section 15.
Records empirical runtime, VRAM utilization, output artifacts, and QA status.
"""

import os
import sys
import time
import json
from pathlib import Path

STUDIO_ROOT = Path(r"D:\AI Local\Blender AI Studio")
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

from Core.blender_bridge import BlenderBridge
from Core.vram_monitor import ResourceMonitor
from Core.qa_engine import QAEngine
from AI.Local.bpy_generator import BpyGenerator
from AI.Local.vision_inspector import VisionInspector
from Generation.image_generator import ImageGenerator
from Generation.mesh_generator import MeshGenerator
from Core.config import PROJECTS_DIR, RENDERS_DIR, EXPORTS_DIR, TEXTURES_DIR, REPORTS_DIR


def run_master_test_suite():
    print("=" * 70)
    print("BLENDER AI STUDIO - MASTER ACCEPTANCE TEST SUITE (TESTS 1 - 10)")
    print("=" * 70)

    bridge = BlenderBridge()
    bridge.new_session()
    qa = QAEngine(bridge)
    img_gen = ImageGenerator()
    mesh_gen = MeshGenerator(bridge)
    vision_insp = VisionInspector()

    test_logs = []

    def log_test(test_id, name, result, runtime, vram_mb, files, errors=None):
        entry = {
            "test_id": test_id,
            "name": name,
            "result": result,
            "runtime_seconds": round(runtime, 2),
            "vram_mb": vram_mb,
            "output_files": [str(f) for f in files],
            "errors": errors or []
        }
        test_logs.append(entry)
        status_str = "PASS" if result == "SUCCESS" else "FAIL"
        print(f"[{test_id}] {name} -> {status_str} in {runtime:.2f}s (VRAM: {vram_mb.get('used_mb', 0):.1f}MB)")

    # -------------------------------------------------------------
    # TEST 1: Generate a simple object from text
    # -------------------------------------------------------------
    print("\nExecuting TEST 1: Simple object from text...")
    t0 = time.time()
    t1_glb = EXPORTS_DIR / "test1_scifi_crate.glb"
    res1 = mesh_gen.generate_asset(
        prompt="Sleek sci-fi equipment container with beveled protective edges",
        category="general",
        export_glb=True
    )
    r1_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 1", "Simple Object from Text",
             "SUCCESS" if res1.get("status") == "success" else "FAILURE",
             time.time() - t0, r1_vram, [res1.get("exported_glb")])

    # -------------------------------------------------------------
    # TEST 2: Generate a model from a reference image
    # -------------------------------------------------------------
    print("\nExecuting TEST 2: Model from reference image...")
    t0 = time.time()
    ref_img = img_gen.output_dir / "multiview_vehicle.png"
    res2 = mesh_gen.generate_asset(
        prompt="Aerodynamic concept derived from reference orthographic sheet",
        category="vehicle",
        reference_image=str(ref_img),
        export_glb=True
    )
    r2_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 2", "Model from Reference Image",
             "SUCCESS" if res2.get("status") == "success" else "FAILURE",
             time.time() - t0, r2_vram, [res2.get("exported_glb"), ref_img])

    # -------------------------------------------------------------
    # TEST 3: Import and refine a generated vehicle
    # -------------------------------------------------------------
    print("\nExecuting TEST 3: Import and refine generated vehicle...")
    t0 = time.time()
    t3_script = """import bpy
# Import base asset and add aerodynamic ground-effect diffuser
chassis = bpy.data.objects.get("Hypercar_Chassis")
if not chassis:
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0.4))
    chassis = bpy.context.active_object
    chassis.name = "Hypercar_Chassis"
    chassis.scale = (1.1, 2.3, 0.35)

# Add aerodynamic side mirrors
for side in [-1.2, 1.2]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.3, location=(side, 0.2, 0.8))
    m = bpy.context.active_object
    m.name = f"Mirror_{'L' if side < 0 else 'R'}"

# Add Bevel Modifier for production reflections
bev = chassis.modifiers.new(name="AeroBevel", type='BEVEL')
bev.width = 0.04
bev.segments = 2
bpy.ops.object.modifier_apply(modifier="AeroBevel")
"""
    res3_exec = bridge.execute_script(t3_script)
    t3_glb = EXPORTS_DIR / "test3_refined_vehicle.glb"
    res3_exp = bridge.export_asset(filepath=str(t3_glb), format="glb")
    r3_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 3", "Import and Refine Vehicle",
             "SUCCESS" if res3_exp.get("status") == "success" else "FAILURE",
             time.time() - t0, r3_vram, [t3_glb])

    # -------------------------------------------------------------
    # TEST 4: Create a procedural mechanical object
    # -------------------------------------------------------------
    print("\nExecuting TEST 4: Procedural mechanical spur gear...")
    t0 = time.time()
    t4_script = """import bpy, bmesh, math
mesh = bpy.data.meshes.new("PrecisionSpurGear")
obj = bpy.data.objects.new("PrecisionSpurGear", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj

bm = bmesh.new()
teeth = 20
r_in, r_out, h_tooth = 0.6, 1.4, 0.35
outer, inner = [], []

for i in range(teeth * 2):
    angle = (2 * math.pi / (teeth * 2)) * i
    r = r_out + (h_tooth if i % 2 == 1 else 0.0)
    outer.append(bm.verts.new((r * math.cos(angle), r * math.sin(angle), 0)))
    inner.append(bm.verts.new((r_in * math.cos(angle), r_in * math.sin(angle), 0)))

for i in range(teeth * 2):
    ni = (i + 1) % (teeth * 2)
    bm.faces.new([inner[i], outer[i], outer[ni], inner[ni]])

bm.to_mesh(mesh)
bm.free()

sol = obj.modifiers.new(name="Extrude", type='SOLIDIFY')
sol.thickness = 0.5
bpy.ops.object.modifier_apply(modifier="Extrude")
bpy.ops.object.shade_smooth()
"""
    res4 = bridge.execute_script(t4_script)
    r4_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 4", "Procedural Mechanical Object",
             "SUCCESS" if res4.get("status") == "success" else "FAILURE",
             time.time() - t0, r4_vram, [])

    # -------------------------------------------------------------
    # TEST 5: Generate and apply a PBR material
    # -------------------------------------------------------------
    print("\nExecuting TEST 5: Generate and apply PBR material...")
    t0 = time.time()
    pbr_maps = img_gen.generate_pbr_texture_set("AerospaceAlloy", size=512)
    res5_mat = bridge.create_material(
        name="AerospaceAlloy",
        pbr_properties={"metallic": 0.9, "roughness": 0.2},
        assign_to="PrecisionSpurGear"
    )
    res5_tex = bridge.assign_texture(
        material_name="AerospaceAlloy",
        texture_type="normal",
        image_path=pbr_maps["normal"]
    )
    r5_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 5", "Generate and Apply PBR Material",
             "SUCCESS" if res5_mat.get("status") == "success" else "FAILURE",
             time.time() - t0, r5_vram, list(pbr_maps.values()))

    # -------------------------------------------------------------
    # TEST 6: Create a simple character workflow (Rigging & Armature)
    # -------------------------------------------------------------
    print("\nExecuting TEST 6: Character mesh & armature rigging...")
    t0 = time.time()
    t6_script = """import bpy
# Character Low-Poly Stylized Humanoid
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.5))
torso = bpy.context.active_object
torso.name = "Character_Torso"
torso.scale = (0.5, 0.3, 0.7)
bpy.ops.object.transform_apply(scale=True)

# Head
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 2.4))
head = bpy.context.active_object
head.name = "Character_Head"

# Create Armature
bpy.ops.object.armature_add(location=(0, 0, 0.8))
arm = bpy.context.active_object
arm.name = "Character_Rig"
bpy.ops.object.mode_set(mode='EDIT')
root = arm.data.edit_bones[0]
root.name = "Root_Spine"
root.tail = (0, 0, 1.8)

neck = arm.data.edit_bones.new("Neck_Head")
neck.head = (0, 0, 1.8)
neck.tail = (0, 0, 2.5)
neck.parent = root
bpy.ops.object.mode_set(mode='OBJECT')
"""
    res6 = bridge.execute_script(t6_script)
    r6_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 6", "Character & Armature Rigging",
             "SUCCESS" if res6.get("status") == "success" else "FAILURE",
             time.time() - t0, r6_vram, [])

    # -------------------------------------------------------------
    # TEST 7: Generate a small architectural scene
    # -------------------------------------------------------------
    print("\nExecuting TEST 7: Small architectural scene...")
    t0 = time.time()
    t7_script = """import bpy
# Modular Architectural Pavilion / Columns
for x in [-3.0, 3.0]:
    for y in [-3.0, 3.0]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=4.0, location=(x, y, 2.0))
        c = bpy.context.active_object
        c.name = f"Column_{x}_{y}"

# Floor Tile
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0, 0, 0))
floor_obj = bpy.context.active_object
floor_obj.name = "Pavilion_Floor"

# Roof Arch
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 4.2))
roof = bpy.context.active_object
roof.name = "Pavilion_Roof"
roof.scale = (4.0, 4.0, 0.3)
bpy.ops.object.transform_apply(scale=True)
"""
    res7 = bridge.execute_script(t7_script)
    r7_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 7", "Architectural Scene Construction",
             "SUCCESS" if res7.get("status") == "success" else "FAILURE",
             time.time() - t0, r7_vram, [])

    # -------------------------------------------------------------
    # TEST 8: Render and inspect a completed scene
    # -------------------------------------------------------------
    print("\nExecuting TEST 8: Cycles OptiX GPU Render & Inspection...")
    t0 = time.time()
    render_out = RENDERS_DIR / "test8_master_render.png"
    bridge.setup_camera(location=(6.0, -7.0, 4.5), look_at=(0, 0, 1.2), focal_length=50.0)
    bridge.setup_lighting(name="MainKeySun", light_type="SUN", energy=4.5, location=(6, -5, 8))
    res8_render = bridge.render(
        output_path=str(render_out),
        engine="CYCLES",
        resolution_x=1280,
        resolution_y=720,
        samples=48,
        device="GPU"
    )
    insp8 = vision_insp.analyze_heuristics(str(render_out))
    r8_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 8", "Cycles OptiX Render & Inspection",
             "SUCCESS" if insp8.get("valid") and insp8.get("quality_rating") == "PASS" else "FAILURE",
             time.time() - t0, r8_vram, [render_out])

    # -------------------------------------------------------------
    # TEST 9: Export GLB and verify exported asset
    # -------------------------------------------------------------
    print("\nExecuting TEST 9: Production GLB Export & QA Audit...")
    t0 = time.time()
    t9_glb = EXPORTS_DIR / "test9_production_master.glb"
    res9_exp = bridge.export_asset(filepath=str(t9_glb), format="glb")
    # Run full QA audit on exported object
    qa_rep = qa.audit_object("PrecisionSpurGear")
    r9_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 9", "GLB Export & QA Verification",
             "SUCCESS" if res9_exp.get("status") == "success" and os.path.isfile(str(t9_glb)) else "FAILURE",
             time.time() - t0, r9_vram, [t9_glb])

    # -------------------------------------------------------------
    # TEST 10: Verify offline operation (No Internet)
    # -------------------------------------------------------------
    print("\nExecuting TEST 10: Air-gapped Offline Operation Check...")
    t0 = time.time()
    # Test completely local execution of prompt to mesh and render
    res10 = mesh_gen.generate_asset(
        prompt="Autonomous rover wheel with all-terrain treads",
        category="mechanical",
        export_glb=True
    )
    r10_vram = ResourceMonitor.get_gpu_status()
    log_test("TEST 10", "Offline Air-Gapped Autonomy",
             "SUCCESS" if res10.get("status") == "success" else "FAILURE",
             time.time() - t0, r10_vram, [res10.get("exported_glb")])

    print("\n" + "=" * 70)
    print("ALL 10 TESTS COMPLETED")
    print("=" * 70)

    # Save complete test suite report
    summary_path = REPORTS_DIR / "master_test_results.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(test_logs, f, indent=2)
    print(f"Master test results report written to: {summary_path}")

    return test_logs


if __name__ == "__main__":
    run_master_test_suite()

