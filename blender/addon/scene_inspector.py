"""Blender addon scene inspection helper."""

import bpy
from typing import Dict, Any

def get_quick_status() -> Dict[str, Any]:
    """Return quick status for the N-panel display."""
    active_obj = bpy.context.view_layer.objects.active
    return {
        "object_count": len(bpy.context.scene.objects),
        "active_object": active_obj.name if active_obj else "None",
        "mode": bpy.context.mode,
        "engine": bpy.context.scene.render.engine
    }
