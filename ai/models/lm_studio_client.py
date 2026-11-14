"""OpenAI-compatible client for LM Studio running on localhost:1234."""

import requests
import json
from typing import Dict, List, Any, Optional
from config.model_config import LM_STUDIO_API_URL
from core.logger import logger

class LMStudioClient:
    def __init__(self, base_url: str = LM_STUDIO_API_URL, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> bool:
        """Check whether LM Studio API server is responding."""
        try:
            r = requests.get(f"{self.base_url}/models", timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """List currently loaded or available models from LM Studio."""
        try:
            r = requests.get(f"{self.base_url}/models", timeout=self.timeout)
            if r.status_code == 200:
                data = r.json()
                return data.get("data", [])
            return []
        except Exception as e:
            logger.debug(f"Could not retrieve models from LM Studio: {e}")
            return []

    def chat_completion(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None,
                        model: Optional[str] = None, temperature: float = 0.2) -> Dict[str, Any]:
        """Send chat completion with optional tool definitions."""
        payload = {
            "messages": messages,
            "temperature": temperature,
        }
        if model:
            payload["model"] = model
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout
            )
            if r.status_code == 200:
                return r.json()
            return {"error": f"LM Studio returned HTTP {r.status_code}: {r.text}"}
        except Exception as e:
            return {"error": f"LM Studio request failed: {e}"}
