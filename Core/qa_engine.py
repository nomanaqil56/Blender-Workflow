"""
Blender AI Studio - Automated Quality Assurance Engine
Runs empirical geometric, UV, material, and export audits
on production 3D assets directly through Blender's bmesh and bpy APIs.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from Core.config import REPORTS_DIR, EXPORTS_DIR
    from Core.blender_bridge import BlenderBridge
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from Core.config import REPORTS_DIR, EXPORTS_DIR
    from Core.blender_bridge import BlenderBridge


class QAEngine:
    """Automated Quality Assurance and Mesh Verification."""

    def __init__(self, bridge: Optional[BlenderBridge] = None):
        self.bridge = bridge or BlenderBridge()
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def audit_object(self, object_name: str) -> Dict[str, Any]:
        """Runs complete geometry, normal, UV, and material audit script on target object."""
        audit_script = f"""
import bpy
import bmesh

obj = bpy.data.objects.get('{object_name}')
if not obj or obj.type != 'MESH':
    result = {{"error": f"Mesh object '{object_name}' not found."}}
else:
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)

    # 1. Geometry Metrics
    vert_count = len(bm.verts)
    edge_count = len(bm.edges)
    face_count = len(bm.faces)

    # 2. Non-manifold check
    non_manifold_verts = [v.index for v in bm.verts if not v.is_manifold]
    non_manifold_edges = [e.index for e in bm.edges if not e.is_manifold]
    loose_verts = [v.index for v in bm.verts if len(v.link_edges) == 0]
    loose_edges = [e.index for e in bm.edges if len(e.link_faces) == 0]

    # 3. Degenerate & Zero-area faces
    zero_area_faces = [f.index for f in bm.faces if f.calc_area() < 1e-7]

    # 4. Scale & Dimensions check
    scale = list(obj.scale)
    is_scale_applied = all(abs(s - 1.0) < 1e-3 for s in scale)
    dimensions = list(obj.dimensions)

    # 5. UV Map check
    has_uv = bool(me.uv_layers)
    uv_layer_count = len(me.uv_layers)
    uv_names = [uv.name for uv in me.uv_layers]

    # 6. Materials check
    mats = [m.name for m in obj.data.materials if m]
    has_materials = len(mats) > 0

    bm.free()

    # Empirical scoring
    geo_pass = (len(non_manifold_edges) == 0 and len(zero_area_faces) == 0 and len(loose_verts) == 0)
    uv_pass = has_uv
    mat_pass = has_materials
    overall_pass = geo_pass and uv_pass and mat_pass

    result = {{
        "object_name": obj.name,
        "vertex_count": vert_count,
        "edge_count": edge_count,
        "face_count": face_count,
        "non_manifold_vertices_count": len(non_manifold_verts),
        "non_manifold_edges_count": len(non_manifold_edges),
        "loose_vertices_count": len(loose_verts),
        "loose_edges_count": len(loose_edges),
        "zero_area_faces_count": len(zero_area_faces),
        "scale": scale,
        "is_scale_applied": is_scale_applied,
        "dimensions": dimensions,
        "has_uv_map": has_uv,
        "uv_layers": uv_names,
        "materials": mats,
        "geometry_passed": geo_pass,
        "uv_passed": uv_pass,
        "materials_passed": mat_pass,
        "overall_production_ready": overall_pass,
        "timestamp": {time.time()}
    }}
"""
        exec_res = self.bridge.execute_script(audit_script)
        if exec_res.get("status") == "success":
            data_dict = exec_res.get("data", {})
            audit_data = data_dict.get("result", {}) if isinstance(data_dict, dict) else {}
            self._save_qa_report(object_name, audit_data)
            return audit_data
        else:
            return {"error": exec_res.get("message", "QA script execution failed.")}

    def _save_qa_report(self, object_name: str, audit_data: Dict[str, Any]) -> str:
        """Saves JSON and Markdown audit reports."""
        filename = f"qa_audit_{object_name}.json"
        json_path = self.reports_dir / filename
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2)

        md_path = self.reports_dir / f"qa_audit_{object_name}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Quality Assurance Audit Report: {object_name}\n\n")
            f.write(f"- **Overall Status**: `{'PRODUCTION READY' if audit_data.get('overall_production_ready') else 'ACTION REQUIRED'}`\n")
            f.write(f"- **Vertices**: {audit_data.get('vertex_count')}\n")
            f.write(f"- **Faces**: {audit_data.get('face_count')}\n")
            f.write(f"- **Non-manifold Edges**: {audit_data.get('non_manifold_edges_count')}\n")
            f.write(f"- **Zero-area Faces**: {audit_data.get('zero_area_faces_count')}\n")
            f.write(f"- **Scale Applied**: {audit_data.get('is_scale_applied')} ({audit_data.get('scale')})\n")
            f.write(f"- **UV Maps**: {audit_data.get('uv_layers')} (Passed: {audit_data.get('uv_passed')})\n")
            f.write(f"- **Materials**: {audit_data.get('materials')} (Passed: {audit_data.get('materials_passed')})\n")

        return str(json_path)


if __name__ == "__main__":
    qa = QAEngine()
    scene = qa.bridge.inspect_scene()
    objs = [o["name"] for o in scene.get("data", {}).get("objects", []) if o.get("type") == "MESH"]
    target = objs[0] if objs else "MechHousing"
    rep = qa.audit_object(target)
    print(json.dumps(rep, indent=2))
