"""Camera creation, tracking, and composition tools."""

import bpy
import math
from typing import Dict, Any, List, Optional

def setup_camera(camera_name: str = "Studio_Camera", location: Optional[List[float]] = None,
                 rotation: Optional[List[float]] = None, target_object: str = "",
                 focal_length: float = 50.0, set_as_active: bool = True, **kwargs) -> Dict[str, Any]:
    """Create or reposition a camera and frame target object."""
    cam_obj = bpy.data.objects.get(camera_name)
    if not cam_obj or cam_obj.type != 'CAMERA':
        cam_data = bpy.data.cameras.new(name=camera_name + "_data")
        cam_obj = bpy.data.objects.new(camera_name, cam_data)
        bpy.context.collection.objects.link(cam_obj)

    cam_obj.data.lens = focal_length

    if location is not None:
        cam_obj.location = tuple(location)
    else:
        cam_obj.location = (3.5, -4.0, 2.5)

    if rotation is not None:
        cam_obj.rotation_euler = tuple(rotation)

    # Track to target object if specified
    if target_object:
        target = bpy.data.objects.get(target_object)
        if target:
            # Remove existing track constraint if any
            for c in list(cam_obj.constraints):
                if c.type == 'TRACK_TO':
                    cam_obj.constraints.remove(c)
            constraint = cam_obj.constraints.new(type='TRACK_TO')
            constraint.target = target
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'

    if set_as_active:
        bpy.context.scene.camera = cam_obj

    return {
        "status": "SUCCESS",
        "camera_name": cam_obj.name,
        "location": list(cam_obj.location),
        "focal_length": focal_length,
        "is_active_scene_camera": bpy.context.scene.camera == cam_obj
    }
