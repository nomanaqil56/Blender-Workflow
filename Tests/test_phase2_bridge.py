"""
Phase 2 Validation Test Suite
Tests all core Blender operations through the BlenderBridge.
"""

import os
import sys
import json
import time
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(r"D:\AI Local\Blender AI Studio")
sys.path.append(str(PROJECT_ROOT))

from Core.blender_bridge import BlenderBridge
from Core.config import PROJECTS_DIR, RENDERS_DIR, EXPORTS_DIR, TEMP_DIR
from Core.vram_monitor import ResourceMonitor

def run_phase2_test():
    print("=" * 60)
    print("PHASE 2 - BLENDER INTEGRATION VALIDATION SUITE")
    print("=" * 60)
    
    bridge = BlenderBridge()
    bridge.new_session()
    results = {}
    start_time = time.time()
    
    # Check baseline resource status
    vram_before = ResourceMonitor.get_gpu_status()
    print(f"[Init] Initial VRAM Free: {vram_before['free_mb']} MB")

    # 1. Scene Inspection
    print("\n[Step 1] Inspecting initial scene...")
    t0 = time.time()
    resp1 = bridge.inspect_scene()
    assert resp1.get("status") == "success", f"Scene inspection failed: {resp1}"
    print(f" -> Scene objects count: {resp1['data']['objects_count']}, Time: {time.time()-t0:.2f}s")
    results["step1_inspect"] = resp1

    # 2. Object Creation
    print("\n[Step 2] Creating mechanical base mesh (Cylinder)...")
    t0 = time.time()
    resp2 = bridge.create_object(obj_type="cylinder", name="MechHousing", location=(0, 0, 1), size=2.0)
    assert resp2.get("status") == "success", f"Object creation failed: {resp2}"
    print(f" -> Created object: {resp2['data']['name']}, Time: {time.time()-t0:.2f}s")
    results["step2_create"] = resp2

    # 3. Object Modification
    print("\n[Step 3] Modifying object scale & position...")
    t0 = time.time()
    resp3 = bridge.modify_object(name="MechHousing", scale=(1.2, 1.2, 0.8), apply_transforms=True)
    assert resp3.get("status") == "success", f"Modification failed: {resp3}"
    print(f" -> Transformed: {resp3['data']['name']}, Scale: {resp3['data']['scale']}, Time: {time.time()-t0:.2f}s")
    results["step3_modify"] = resp3

    # 4. Mesh Operations
    print("\n[Step 4] Applying mesh operations (Subdivide & Recalculate Normals)...")
    t0 = time.time()
    resp4_sub = bridge.mesh_operations(name="MechHousing", action="subdivide", params={"cuts": 1})
    resp4_norm = bridge.mesh_operations(name="MechHousing", action="recalculate_normals")
    resp4_smooth = bridge.mesh_operations(name="MechHousing", action="shade_smooth")
    assert resp4_sub.get("status") == "success", f"Subdivision failed: {resp4_sub}"
    print(f" -> Vertices count: {resp4_sub['data']['vertices_count']}, Time: {time.time()-t0:.2f}s")
    results["step4_mesh_ops"] = resp4_sub

    # 5. PBR Material Creation
    print("\n[Step 5] Creating PBR Metallic Carbon/Chrome Material...")
    t0 = time.time()
    pbr_props = {
        "base_color": (0.05, 0.15, 0.25),
        "metallic": 0.9,
        "roughness": 0.15,
        "emission_color": (0.0, 0.5, 1.0),
        "emission_strength": 0.5
    }
    resp5 = bridge.create_material(name="TitaniumAlloy", pbr_properties=pbr_props, assign_to="MechHousing")
    assert resp5.get("status") == "success", f"Material creation failed: {resp5}"
    print(f" -> Material: {resp5['data']['material_name']} assigned to {resp5['data']['assigned_to']}, Time: {time.time()-t0:.2f}s")
    results["step5_material"] = resp5

    # 6. Lighting Setup
    print("\n[Step 6] Setting up studio key & rim lighting...")
    t0 = time.time()
    resp6_key = bridge.setup_lighting(name="KeyLight", light_type="SUN", energy=4.0, location=(4, -4, 6), color=(1.0, 0.95, 0.9))
    resp6_rim = bridge.setup_lighting(name="RimLight", light_type="AREA", energy=250.0, location=(-4, 4, 3), color=(0.4, 0.7, 1.0))
    assert resp6_key.get("status") == "success", f"Lighting failed: {resp6_key}"
    print(f" -> Key and rim lights established, Time: {time.time()-t0:.2f}s")
    results["step6_lighting"] = resp6_key

    # 7. Camera Positioning
    print("\n[Step 7] Setting up cinematography camera pointing at target...")
    t0 = time.time()
    resp7 = bridge.setup_camera(name="MainCamera", location=(4.5, -4.5, 3.5), look_at=(0, 0, 1), focal_length=65.0)
    assert resp7.get("status") == "success", f"Camera setup failed: {resp7}"
    print(f" -> Camera lens: {resp7['data']['focal_length']}mm, Location: {resp7['data']['location']}, Time: {time.time()-t0:.2f}s")
    results["step7_camera"] = resp7

    # 8. Geometry Nodes
    print("\n[Step 8] Applying procedural Geometry Nodes modifier...")
    t0 = time.time()
    resp8 = bridge.apply_geometry_nodes(object_name="MechHousing", node_graph_type="subdivision", params={"level": 1})
    assert resp8.get("status") == "success", f"Geometry nodes failed: {resp8}"
    print(f" -> Geometry Nodes modifier: {resp8['data']['modifier']}, Time: {time.time()-t0:.2f}s")
    results["step8_geonodes"] = resp8

    # 9. Rendering (Cycles GPU / OptiX)
    render_file = RENDERS_DIR / "phase2_render.png"
    print(f"\n[Step 9] Rendering scene to {render_file} via Cycles OptiX...")
    t0 = time.time()
    resp9 = bridge.render(output_path=str(render_file), engine="CYCLES", resolution_x=960, resolution_y=540, samples=32, device="GPU")
    assert resp9.get("status") == "success", f"Render failed: {resp9}"
    print(f" -> Rendered in {time.time()-t0:.2f}s: {resp9['data']['filepath']}")
    results["step9_render"] = resp9

    # 10. Inspect Render
    print("\n[Step 10] Inspecting render output...")
    t0 = time.time()
    resp10 = bridge.inspect_render(image_path=str(render_file))
    assert resp10.get("status") == "success", f"Render inspection failed: {resp10}"
    print(f" -> Render verified: {resp10['data']['resolution'][0]}x{resp10['data']['resolution'][1]}, Size: {resp10['data']['size_bytes']} bytes, Time: {time.time()-t0:.2f}s")
    results["step10_inspect_render"] = resp10

    # 11. Save Project
    project_file = PROJECTS_DIR / "phase2_scene.blend"
    print(f"\n[Step 11] Saving Blender project to {project_file}...")
    t0 = time.time()
    resp11 = bridge.save_project(filepath=str(project_file))
    assert resp11.get("status") == "success", f"Save project failed: {resp11}"
    print(f" -> Project saved: {resp11['data']['filepath']}, Time: {time.time()-t0:.2f}s")
    results["step11_save"] = resp11

    # 12. Export GLB Asset
    export_file = EXPORTS_DIR / "phase2_mech.glb"
    print(f"\n[Step 12] Exporting production GLB asset to {export_file}...")
    t0 = time.time()
    resp12 = bridge.export_asset(filepath=str(export_file), format="glb")
    assert resp12.get("status") == "success", f"Export failed: {resp12}"
    print(f" -> Asset exported: {resp12['data']['filepath']}, Size: {resp12['data']['size_bytes']} bytes, Time: {time.time()-t0:.2f}s")
    results["step12_export"] = resp12

    # Measure final resource state
    vram_after = ResourceMonitor.get_gpu_status()
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("PHASE 2 VALIDATION COMPLETED SUCCESSFULLY")
    print(f"Total Execution Time: {total_time:.2f}s")
    print(f"VRAM Peak Used: {vram_after['used_mb']} MB (Free: {vram_after['free_mb']} MB)")
    print("=" * 60)

    # Save summary report
    report_file = PROJECT_ROOT / "Reports" / "phase2_validation_report.json"
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "total_time_seconds": total_time,
            "vram_status": vram_after,
            "results": results
        }, f, indent=2)
    print(f"Report written to: {report_file}")

if __name__ == "__main__":
    run_phase2_test()
