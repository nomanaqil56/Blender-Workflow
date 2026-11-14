"""Conversation message and prompt history persistence."""

import json
from pathlib import Path
from typing import List, Dict, Any
from config.settings import REPORTS_DIR

class ConversationStore:
    def __init__(self):
        self.store_file = REPORTS_DIR / "conversation_history.json"
        self._history: List[Dict[str, str]] = self._load()

    def _load(self) -> List[Dict[str, str]]:
        if self.store_file.exists():
            try:
                with open(self.store_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def add_message(self, role: str, content: str):
        self._history.append({"role": role, "content": content})
        try:
            with open(self.store_file, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2)
        except Exception:
            pass

    def get_history(self) -> List[Dict[str, str]]:
        return list(self._history)

conversation_store = ConversationStore()
