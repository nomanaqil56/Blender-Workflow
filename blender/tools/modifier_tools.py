"""Modifier creation, configuration, and baking tools."""

import bpy
from typing import Dict, Any

def add_modifier(object_name: str, modifier_type: str, modifier_name: str = "",
                 properties: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
    """Add a modifier to the target object."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    m_name = modifier_name or modifier_type.capitalize()
    mod = obj.modifiers.new(name=m_name, type=modifier_type)

    if properties:
        for k, v in properties.items():
            if hasattr(mod, k):
                try:
                    setattr(mod, k, v)
                except Exception as e:
                    return {"status": "ERROR", "message": f"Could not set {k}={v} on modifier: {e}"}

    return {
        "status": "SUCCESS",
        "object_name": obj.name,
        "modifier_name": mod.name,
        "modifier_type": mod.type
    }

def configure_modifier(object_name: str, modifier_name: str, properties: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Update properties on an existing modifier."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    mod = obj.modifiers.get(modifier_name)
    if not mod:
        return {"status": "ERROR", "message": f"Modifier '{modifier_name}' not found on object '{object_name}'."}

    for k, v in properties.items():
        if hasattr(mod, k):
            setattr(mod, k, v)

    return {"status": "SUCCESS", "object_name": obj.name, "modifier_name": mod.name, "updated": properties}

def apply_modifier(object_name: str, modifier_name: str, **kwargs) -> Dict[str, Any]:
    """Permanently apply a modifier."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        return {"status": "ERROR", "message": f"Object '{object_name}' not found."}

    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        return {"status": "SUCCESS", "object_name": obj.name, "applied_modifier": modifier_name}
    except Exception as e:
        return {"status": "ERROR", "message": f"Failed to apply modifier '{modifier_name}': {e}"}
