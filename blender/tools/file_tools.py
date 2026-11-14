"""Project saving and 3D asset export tools."""

import bpy
from pathlib import Path
from typing import Dict, Any
from config.settings import PROJECTS_DIR, EXPORTS_DIR

def save_project(filepath: str = "", **kwargs) -> Dict[str, Any]:
    """Save current scene to blend file."""
    if not filepath:
        target = PROJECTS_DIR / "blender_ai_studio_autosave.blend"
    else:
        target = Path(filepath)
        if not target.is_absolute():
            target = PROJECTS_DIR / filepath

    target.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(target))

    return {
        "status": "SUCCESS",
        "filepath": str(target)
    }

def export_asset(filepath: str, format: str = "glb", selected_only: bool = False, **kwargs) -> Dict[str, Any]:
    """Export scene or selected object to GLB/OBJ/FBX."""
    target = Path(filepath)
    if not target.is_absolute():
        clean_name = target.name
        target = EXPORTS_DIR / clean_name
    target.parent.mkdir(parents=True, exist_ok=True)

    fmt = format.lower()
    if fmt in ["glb", "gltf"]:
        bpy.ops.export_scene.gltf(
            filepath=str(target),
            export_format='GLB',
            use_selection=selected_only,
            export_apply=True
        )
    elif fmt == "obj":
        bpy.ops.wm.obj_export(filepath=str(target), export_selected_objects=selected_only)
    elif fmt == "fbx":
        bpy.ops.export_scene.fbx(filepath=str(target), use_selection=selected_only)
    else:
        return {"status": "ERROR", "message": f"Unsupported export format: {format}"}

    return {
        "status": "SUCCESS",
        "filepath": str(target),
        "format": fmt,
        "filesize_bytes": target.stat().st_size if target.exists() else 0
    }
