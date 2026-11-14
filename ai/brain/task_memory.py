"""Persistent task and object memory across multi-turn interactions."""

from typing import Dict, List, Any, Optional

class TaskMemory:
    def __init__(self):
        self.instruction_history: List[str] = []
        self.object_catalog: Dict[str, Dict[str, Any]] = {}
        self.last_target_object: Optional[str] = None

    def remember_instruction(self, instruction: str):
        self.instruction_history.append(instruction)

    def register_object(self, name: str, category: str, details: Dict[str, Any] = None):
        self.object_catalog[name] = {
            "name": name,
            "category": category,
            "details": details or {},
        }
        self.last_target_object = name

    def update_object_details(self, name: str, updates: Dict[str, Any]):
        if name in self.object_catalog:
            self.object_catalog[name]["details"].update(updates)

    def resolve_target_object(self, query: str) -> Optional[str]:
        """Resolve pronouns like 'it', 'the model', 'the ball' to known objects."""
        q = query.lower()
        if "gear" in q:
            for name, meta in self.object_catalog.items():
                if "gear" in name.lower() or meta.get("category") == "gear":
                    return name
        if "ball" in q or "football" in q:
            for name, meta in self.object_catalog.items():
                if "football" in name.lower() or meta.get("category") == "football":
                    return name
        # Default to last referenced/created object
        return self.last_target_object

task_memory = TaskMemory()
