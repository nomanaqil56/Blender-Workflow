"""Test Suite: Visual Intelligence Pipeline and Correction Loop."""

import unittest
from ai.vision.vision_manager import vision_manager
from ai.vision.result_evaluator import result_evaluator
from blender.controller.blender_controller import blender_controller

class TestVisualFeedback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blender_controller.connect()

    def test_01_viewport_capture_and_analysis(self):
        """Capture and analyze viewport image."""
        res = vision_manager.inspect_current_viewport("test_visual_capture.png")
        self.assertEqual(res.get("status"), "SUCCESS")
        metrics = res.get("metrics", {})
        self.assertIn("avg_luminance", metrics)
        self.assertIn("contrast_score", metrics)
        self.assertGreater(metrics.get("width", 0), 100)

    def test_02_defect_detection_and_lighting_evaluation(self):
        """Verify result evaluator flags defects and generates recommendations."""
        # Simulated dark/flat scene metrics
        imperfect_metrics = {
            "avg_luminance": 0.05,
            "contrast_score": 0.03,
            "is_underexposed": True,
            "is_overexposed": False,
            "is_flat_contrast": True
        }
        eval_res = result_evaluator.evaluate(imperfect_metrics)
        self.assertFalse(eval_res["is_satisfactory"])
        self.assertGreater(len(eval_res["defects"]), 0)
        self.assertIn("underexposed", eval_res["defects"][0].lower())
        self.assertGreater(len(eval_res["corrections"]), 0)

        # Well-lit scene metrics
        perfect_metrics = {
            "avg_luminance": 0.45,
            "contrast_score": 0.22,
            "is_underexposed": False,
            "is_overexposed": False,
            "is_flat_contrast": False
        }
        eval_good = result_evaluator.evaluate(perfect_metrics)
        self.assertTrue(eval_good["is_satisfactory"])
        self.assertEqual(len(eval_good["defects"]), 0)

if __name__ == "__main__":
    unittest.main()
