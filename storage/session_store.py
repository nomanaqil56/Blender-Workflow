"""Blender AI Studio session history log."""

import time
import json
from pathlib import Path
from typing import Dict, Any
from config.settings import REPORTS_DIR

class SessionStore:
    def __init__(self):
        self.session_log = REPORTS_DIR / "session_log.json"

    def record_session(self, session_summary: Dict[str, Any]):
        sessions = []
        if self.session_log.exists():
            try:
                with open(self.session_log, "r", encoding="utf-8") as f:
                    sessions = json.load(f)
            except Exception:
                sessions = []
        session_summary["timestamp"] = time.time()
        sessions.append(session_summary)
        with open(self.session_log, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2)

session_store = SessionStore()
