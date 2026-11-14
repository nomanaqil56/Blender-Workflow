"""Scene and conversation context tracker for agent reasoning."""

from typing import Dict, Any, List, Optional
from blender.controller.blender_controller import blender_controller

class ContextManager:
    def __init__(self):
        self.active_object_name: Optional[str] = None
        self.last_created_objects: List[str] = []
        self.last_scene_state: Dict[str, Any] = {}

    def refresh_scene_context(self) -> Dict[str, Any]:
        """Query Blender for current scene hierarchy and active object."""
        res = blender_controller.inspect_scene(detailed=True)
        if res.get("status") == "SUCCESS":
            self.last_scene_state = res
            self.active_object_name = res.get("active_object")
        return self.last_scene_state

    def record_created_object(self, name: str):
        if name not in self.last_created_objects:
            self.last_created_objects.append(name)
        self.active_object_name = name

    def get_context_summary(self) -> Dict[str, Any]:
        return {
            "active_object": self.active_object_name,
            "created_objects": list(self.last_created_objects),
            "total_scene_objects": self.last_scene_state.get("total_objects", 0)
        }

context_manager = ContextManager()
