"""Local model catalog and hardware suitability registry."""

from typing import Dict, Any, List
from config.model_config import LOCAL_MODELS, MODELS_ROOT

class ModelRegistry:
    def __init__(self):
        self._models = LOCAL_MODELS

    def get_model_info(self, key: str) -> Dict[str, Any]:
        return self._models.get(key, {})

    def list_models(self) -> List[Dict[str, Any]]:
        result = []
        for key, info in self._models.items():
            path_exists = info.get("path").exists() if "path" in info else False
            result.append({
                "key": key,
                "id": info.get("id"),
                "name": info.get("name"),
                "role": info.get("role"),
                "vram_gb": info.get("vram_estimate_gb", 4.0),
                "is_present_on_disk": path_exists,
                "path": str(info.get("path")) if "path" in info else ""
            })
        return result

model_registry = ModelRegistry()
