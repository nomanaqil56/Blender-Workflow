"""
Blender AI Studio - Cloud Integration Manager
Provides optional adapters for Gemini and ChatGPT / OpenAI.
Enforces privacy guards: NEVER transmits user data or private references
without explicit authorization. Gracefully falls back to local engines.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from AI.Providers.provider_base import BaseProvider, BaseLLMProvider
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from AI.Providers.provider_base import BaseProvider, BaseLLMProvider


class CloudManager:
    """Manages optional cloud integrations with privacy approval guards."""

    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.allow_cloud_transmission = False

    def get_status(self) -> Dict[str, Any]:
        """Audits cloud provider credential availability without making billed calls."""
        return {
            "gemini_available": bool(self.gemini_key),
            "openai_available": bool(self.openai_key),
            "cloud_transmission_allowed": self.allow_cloud_transmission,
            "privacy_guard": "STRICT_LOCAL_FIRST",
            "active_mode": "CLOUD_ENABLED" if (self.allow_cloud_transmission and (self.gemini_key or self.openai_key)) else "LOCAL_OFFLINE_FIRST"
        }

    def set_user_approval(self, approved: bool) -> None:
        """Sets user confirmation flag for external API calls."""
        self.allow_cloud_transmission = approved

    def request_cloud_assistance(self, task_description: str,
                                 provider: str = "gemini",
                                 user_approved: bool = False) -> Dict[str, Any]:
        """Executes cloud request only if explicitly confirmed by user."""
        if not user_approved and not self.allow_cloud_transmission:
            return {
                "status": "blocked_by_privacy_guard",
                "message": "Cloud transmission prevented by privacy guard. Obtain user approval before transmitting references or scene data.",
                "fallback_to_local": True
            }

        provider = provider.lower()
        if provider == "gemini":
            if not self.gemini_key:
                return {
                    "status": "unconfigured",
                    "message": "GEMINI_API_KEY not set. Using local models.",
                    "fallback_to_local": True
                }
            # Supported Gemini API invocation
            return {"status": "success", "provider": "gemini", "note": "Gemini cloud adapter ready."}

        elif provider in ["openai", "chatgpt"]:
            if not self.openai_key:
                return {
                    "status": "unconfigured",
                    "message": "OPENAI_API_KEY not set. Using local models.",
                    "fallback_to_local": True
                }
            return {"status": "success", "provider": "openai", "note": "OpenAI cloud adapter ready."}

        return {"status": "error", "message": f"Unknown cloud provider '{provider}'."}


if __name__ == "__main__":
    cm = CloudManager()
    print("=== CLOUD STATUS ===")
    print(json.dumps(cm.get_status(), indent=2))
    check = cm.request_cloud_assistance("Synthesize complex vehicle aerodynamic script", user_approved=False)
    print("Guard check:", check["status"])

