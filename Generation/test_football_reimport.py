"""
Blender AI Studio - Football GLB Re-import & Verification Test
Re-imports exports/football.glb into a fresh scene and audits geometry & materials.
"""

import sys
import os
import json
from pathlib import Path

STUDIO_ROOT = Path(r"D:\AI Local\Blender AI Studio")
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

GLB_PATH = STUDIO_ROOT / "Exports" / "football.glb"
REIMPORT_BLEND_PATH = STUDIO_ROOT / "Projects" / "Football_Test" / "football_reimported.blend"

REIMPORT_SCRIPT = f"""
import bpy
import bmesh
import json
import os

# Reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Reimport GLB
bpy.ops.import_scene.gltf(filepath=r"{GLB_PATH}")

# Find imported football object
imported_objs = [o for o in bpy.data.objects if o.type == 'MESH']
ball = imported_objs[0] if imported_objs else None

if not ball:
    res = {{"status": "error", "message": "No mesh found in re-imported GLB"}}
else:
    me = ball.data
    bm = bmesh.new()
    bm.from_mesh(me)

    vert_count = len(bm.verts)
    edge_count = len(bm.edges)
    face_count = len(bm.faces)

    non_manifold_verts = len([v for v in bm.verts if not v.is_manifold])
    non_manifold_edges = len([e for e in bm.edges if not e.is_manifold])

    bm.free()

    mats = [m.name for m in ball.data.materials if m]
    has_uv = bool(ball.data.uv_layers)

    res = {{
        "status": "success",
        "object_name": ball.name,
        "vertex_count": vert_count,
        "edge_count": edge_count,
        "face_count": face_count,
        "non_manifold_vertices": non_manifold_verts,
        "non_manifold_edges": non_manifold_edges,
        "materials": mats,
        "materials_count": len(mats),
        "has_uv_map": has_uv,
        "is_manifold": (non_manifold_edges == 0),
        "dimensions": list(ball.dimensions)
    }}

# Save re-imported blend
bpy.ops.wm.save_as_mainfile(filepath=r"{REIMPORT_BLEND_PATH}")

# Output results to file
with open(r"{STUDIO_ROOT / 'Reports' / 'football_reimport_qa.json'}", "w") as f:
    json.dump(res, f, indent=2)
print("Reimport verification complete.")
"""

if __name__ == "__main__":
    runner_script = STUDIO_ROOT / "Generation" / "verify_football_reimport.py"
    with open(runner_script, "w", encoding="utf-8") as f:
        f.write(REIMPORT_SCRIPT)
    print("Verification script written to", runner_script)
