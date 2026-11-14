"""Unified Vision Pipeline manager coordinating capture, analysis, and feedback."""

from pathlib import Path
from typing import Dict, Any, Optional
from ai.vision.image_capture import image_capture
from ai.vision.visual_inspector import visual_inspector
from ai.vision.result_evaluator import result_evaluator
from core.logger import logger

class VisionManager:
    def __init__(self):
        self.capture = image_capture
        self.inspector = visual_inspector
        self.evaluator = result_evaluator

    def inspect_current_viewport(self, filename: str = "visual_inspection.png") -> Dict[str, Any]:
        """Capture and analyze the live viewport frame."""
        img_path = self.capture.capture_viewport(filename)
        if not img_path or not img_path.exists():
            return {"status": "ERROR", "message": "Failed to capture viewport image."}

        metrics = self.inspector.inspect_image(img_path)
        if metrics.get("status") != "SUCCESS":
            return metrics

        evaluation = self.evaluator.evaluate(metrics)
        neural_feedback = self.inspector.inspect_neural(img_path)

        return {
            "status": "SUCCESS",
            "image_path": str(img_path),
            "metrics": metrics,
            "evaluation": evaluation,
            "neural_feedback": neural_feedback
        }

vision_manager = VisionManager()
