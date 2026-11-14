"""Application lifecycle management: initialization and graceful shutdown."""

import atexit
from blender.controller.blender_controller import blender_controller
from ai.models.model_manager import model_manager
from core.logger import logger

class AppLifecycle:
    def initialize(self):
        logger.info("Initializing Blender AI Studio...")
        # Check LM Studio
        model_manager.discover_active_model()
        # Connect to Blender
        blender_controller.connect()
        atexit.register(self.shutdown)
        logger.info("Blender AI Studio initialized.")

    def shutdown(self):
        logger.info("Shutting down Blender AI Studio...")
        blender_controller.disconnect()
        logger.info("Shutdown complete.")

app_lifecycle = AppLifecycle()
