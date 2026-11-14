"""Studio lighting setup and illumination tools."""

import bpy
from typing import Dict, Any, List, Optional

def setup_light(light_name: str, light_type: str = "AREA", energy: float = 500.0,
                color: Optional[List[float]] = None, location: Optional[List[float]] = None,
                rotation: Optional[List[float]] = None, size: float = 2.0, **kwargs) -> Dict[str, Any]:
    """Create or configure a studio light."""
    light_obj = bpy.data.objects.get(light_name)
    if not light_obj or light_obj.type != 'LIGHT':
        light_data = bpy.data.lights.new(name=light_name + "_data", type=light_type)
        light_obj = bpy.data.objects.new(light_name, light_data)
        bpy.context.collection.objects.link(light_obj)
    else:
        light_obj.data.type = light_type

    light_obj.data.energy = energy

    if color is not None:
        c = list(color)[:3]
        light_obj.data.color = tuple(c)

    if location is not None:
        light_obj.location = tuple(location)

    if rotation is not None:
        light_obj.rotation_euler = tuple(rotation)

    if light_type == 'AREA' and hasattr(light_obj.data, 'size'):
        light_obj.data.size = size

    return {
        "status": "SUCCESS",
        "light_name": light_obj.name,
        "type": light_type,
        "energy": energy,
        "location": list(light_obj.location)
    }
