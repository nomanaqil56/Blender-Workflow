"""Checkpoint and rollback manager for undo and state recovery."""

import time
import shutil
from pathlib import Path
from typing import Optional, Dict
from config.settings import PROJECTS_DIR
from core.logger import logger

class CheckpointManager:
    def __init__(self, checkpoint_dir: Optional[Path] = None):
        self.checkpoint_dir = checkpoint_dir or (PROJECTS_DIR / "_checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoints: Dict[str, Path] = {}

    def create_checkpoint(self, task_id: str, step_index: int, source_blend_path: Path) -> Optional[Path]:
        """Save a copy of current blend file as a recoverable checkpoint."""
        if not source_blend_path.exists():
            return None
        cp_name = f"{task_id}_step_{step_index}_{int(time.time())}.blend"
        cp_path = self.checkpoint_dir / cp_name
        try:
            shutil.copy2(source_blend_path, cp_path)
            self._checkpoints[f"{task_id}_{step_index}"] = cp_path
            logger.info(f"Created scene checkpoint: {cp_path.name}")
            return cp_path
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return None

    def get_latest_checkpoint(self, task_id: str) -> Optional[Path]:
        matching = [p for k, p in self._checkpoints.items() if k.startswith(task_id)]
        if not matching:
            return None
        return sorted(matching, key=lambda p: p.stat().st_mtime)[-1]
