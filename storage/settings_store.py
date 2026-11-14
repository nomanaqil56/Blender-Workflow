"""User settings and connection preference persistence."""

import json
from pathlib import Path
from typing import Dict, Any
from config.settings import REPORTS_DIR

class SettingsStore:
    def __init__(self):
        self.settings_file = REPORTS_DIR / "user_settings.json"
        self._settings = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get(self, key: str, default=None):
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        self._settings[key] = value
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2)

settings_store = SettingsStore()
