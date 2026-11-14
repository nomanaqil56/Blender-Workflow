"""Session state tracking for active Blender connection."""

import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from config.settings import PROJECTS_DIR

class SessionManager:
    def __init__(self):
        self.session_id: str = str(uuid.uuid4())[:8]
        self.started_at: float = time.time()
        self.active_file_path: Optional[Path] = None
        self.last_inspect_data: Dict[str, Any] = {}

    def update_from_inspection(self, data: Dict[str, Any]):
        self.last_inspect_data = data

    def get_summary(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "duration_sec": round(time.time() - self.started_at, 1),
            "active_file": str(self.active_file_path) if self.active_file_path else "Unsaved Scene",
            "last_object_count": self.last_inspect_data.get("total_objects", 0),
            "active_object": self.last_inspect_data.get("active_object")
        }

session_manager = SessionManager()
