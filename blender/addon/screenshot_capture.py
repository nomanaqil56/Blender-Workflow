"""Blender addon screenshot helper."""

import bpy
from pathlib import Path
from config.settings import RENDERS_DIR

def capture_active_view(filepath: str = "") -> str:
    """Capture the active 3D viewport."""
    if not filepath:
        out = RENDERS_DIR / "active_viewport.png"
    else:
        out = Path(filepath)
    out.parent.mkdir(parents=True, exist_ok=True)

    old = bpy.context.scene.render.filepath
    bpy.context.scene.render.filepath = str(out)
    try:
        bpy.ops.render.opengl(write_still=True, view='VIEW_3D')
    finally:
        bpy.context.scene.render.filepath = old

    return str(out)
