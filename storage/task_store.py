"""Persistent JSON store for agent tasks and execution history."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from config.settings import REPORTS_DIR

class TaskStore:
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or (REPORTS_DIR / "tasks")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_task(self, task_data: Dict[str, Any]) -> Path:
        task_id = task_data.get("task_id", "unknown_task")
        target = self.storage_dir / f"{task_id}.json"
        with open(target, "w", encoding="utf-8") as f:
            json.dump(task_data, f, indent=2, default=str)
        return target

    def load_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        target = self.storage_dir / f"{task_id}.json"
        if target.exists():
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

task_store = TaskStore()
