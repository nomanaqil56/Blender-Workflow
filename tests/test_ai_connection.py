"""Test Suite: AI Model Discovery and LM Studio Client."""

import unittest
from ai.models.model_registry import model_registry
from ai.models.model_manager import model_manager
from ai.models.lm_studio_client import LMStudioClient

class TestAIConnection(unittest.TestCase):
    def test_01_model_registry_inventory(self):
        """Verify configured models exist on disk in D:\\AI Local."""
        models = model_registry.list_models()
        self.assertGreater(len(models), 0)
        coder = next((m for m in models if m["key"] == "coder"), None)
        self.assertIsNotNone(coder)
        self.assertTrue(coder["is_present_on_disk"], f"Coder model not found at {coder['path']}")

    def test_02_model_manager_status(self):
        """Verify model manager provides hardware and model status."""
        status = model_manager.get_status()
        self.assertIn("api_healthy", status)
        self.assertIn("available_local_models", status)

if __name__ == "__main__":
    unittest.main()
