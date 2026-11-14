"""
Blender AI Studio - Local AI & LM Studio Client
Provides OpenAI-compatible API interface to LM Studio (port 1234)
and local GGUF models on disk (Qwen2.5-Coder, Qwen3.5, DeepSeek-R1).
"""

import sys
import os
import json
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from Core.config import LM_STUDIO_API_URL, LOCAL_MODELS, LM_STUDIO_APP, PROJECT_ROOT
    from Core.vram_monitor import ResourceMonitor
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from Core.config import LM_STUDIO_API_URL, LOCAL_MODELS, LM_STUDIO_APP, PROJECT_ROOT
    from Core.vram_monitor import ResourceMonitor


class LMStudioClient:
    """Client for LM Studio inference server with automatic health checks and model discovery."""

    def __init__(self, api_url: str = LM_STUDIO_API_URL):
        self.api_url = api_url.rstrip("/")

    def check_health(self) -> Dict[str, Any]:
        """Checks if LM Studio's local inference server is responding."""
        try:
            url = f"{self.api_url}/models"
            req = urllib.request.Request(url, headers={"User-Agent": "BlenderAIStudio/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("id") for m in data.get("data", [])]
                return {
                    "online": True,
                    "api_url": self.api_url,
                    "loaded_models": models,
                    "active_model": models[0] if models else None
                }
        except (urllib.error.URLError, ConnectionRefusedError, socket.timeout if 'socket' in globals() else Exception) as e:
            return {
                "online": False,
                "api_url": self.api_url,
                "error": str(e),
                "suggestion": "Start LM Studio and click 'Start Server' on the Local Server tab (port 1234)."
            }

    @staticmethod
    def get_disk_inventory() -> Dict[str, Any]:
        """Catalogs all local GGUF models stored on disk without re-downloading."""
        inventory = {}
        for role, path in LOCAL_MODELS.items():
            exists = path.exists()
            size_gb = round(path.stat().st_size / (1024 ** 3), 2) if exists else 0
            inventory[role] = {
                "path": str(path),
                "exists": exists,
                "size_gb": size_gb,
                "filename": path.name
            }
        return inventory

    def chat_completion(self, messages: List[Dict[str, Any]],
                        model: Optional[str] = None,
                        temperature: float = 0.2,
                        max_tokens: int = 2048,
                        stop: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generates completion from active local model."""
        health = self.check_health()
        if not health["online"]:
            return {
                "status": "offline",
                "message": "LM Studio local server is not running on port 1234.",
                "health": health
            }

        target_model = model or health.get("active_model") or "local-model"
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        if stop:
            payload["stop"] = stop

        try:
            url = f"{self.api_url}/chat/completions"
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json", "User-Agent": "BlenderAIStudio/1.0"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                choice = result["choices"][0]
                return {
                    "status": "success",
                    "model": result.get("model", target_model),
                    "content": choice["message"]["content"],
                    "usage": result.get("usage", {})
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    client = LMStudioClient()
    print("=== DISK MODEL INVENTORY ===")
    print(json.dumps(client.get_disk_inventory(), indent=2))
    print("\n=== LM STUDIO HEALTH CHECK ===")
    print(json.dumps(client.check_health(), indent=2))

