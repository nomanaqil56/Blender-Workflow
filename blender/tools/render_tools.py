"""Render preview and viewport image capture tools."""

import bpy
from pathlib import Path
from typing import Dict, Any, List, Optional
from config.settings import RENDERS_DIR

def render_preview(output_filename: str = "preview.png", samples: int = 64,
                   resolution: Optional[List[int]] = None, engine: str = "CYCLES", **kwargs) -> Dict[str, Any]:
    """Execute high-quality still render."""
    scene = bpy.context.scene
    res = resolution or [1280, 720]

    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]
    scene.render.resolution_percentage = 100

    out_path = Path(output_filename)
    if not out_path.is_absolute():
        out_path = RENDERS_DIR / out_path.name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out_path)

    # Engine config
    if engine == "CYCLES":
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = samples
        # Try GPU compute if available
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            prefs.compute_device_type = 'OPTIX'
            scene.cycles.device = 'GPU'
        except Exception:
            pass
    elif engine in ["BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"]:
        scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'

    bpy.ops.render.render(write_still=True)

    return {
        "status": "SUCCESS",
        "output_path": str(out_path),
        "engine": scene.render.engine,
        "resolution": res,
        "samples": samples
    }

def capture_viewport(output_filename: str = "viewport_capture.png", **kwargs) -> Dict[str, Any]:
    """Capture viewport frame or OpenGL render."""
    out_path = Path(output_filename)
    if not out_path.is_absolute():
        out_path = RENDERS_DIR / out_path.name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    old_filepath = bpy.context.scene.render.filepath
    bpy.context.scene.render.filepath = str(out_path)
    try:
        # Use render opengl view for reliable headless & GUI image capture
        bpy.ops.render.opengl(write_still=True)
    finally:
        bpy.context.scene.render.filepath = old_filepath

    return {
        "status": "SUCCESS",
        "output_path": str(out_path)
    }
