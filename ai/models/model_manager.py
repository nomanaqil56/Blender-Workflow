"""Model lifecycle, discovery, and active model selection."""

from typing import Dict, Any, List, Optional
from ai.models.lm_studio_client import LMStudioClient
from ai.models.model_registry import model_registry
from core.logger import logger

class ModelManager:
    def __init__(self):
        self.client = LMStudioClient()
        self.active_model_id: Optional[str] = None

    def discover_active_model(self) -> Optional[str]:
        """Query LM Studio for currently loaded model."""
        if not self.client.check_health():
            logger.info("LM Studio API is currently offline.")
            return None

        models = self.client.list_models()
        if models:
            self.active_model_id = models[0].get("id")
            logger.info(f"Discovered active LM Studio model: {self.active_model_id}")
            return self.active_model_id
        return None

    def get_status(self) -> Dict[str, Any]:
        healthy = self.client.check_health()
        return {
            "api_healthy": healthy,
            "active_model": self.active_model_id,
            "available_local_models": model_registry.list_models()
        }

model_manager = ModelManager()
