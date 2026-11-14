"""Visual quality evaluation and defect detection."""

from typing import Dict, Any, List

class ResultEvaluator:
    def evaluate(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        defects: List[str] = []
        corrections: List[Dict[str, Any]] = []

        if metrics.get("is_underexposed"):
            defects.append("Scene lighting is underexposed / too dark.")
            corrections.append({
                "type": "LIGHTING",
                "tool": "setup_light",
                "recommended_params": {"energy_multiplier": 2.5}
            })

        if metrics.get("is_overexposed"):
            defects.append("Scene lighting is overexposed / clipped highlights.")
            corrections.append({
                "type": "LIGHTING",
                "tool": "setup_light",
                "recommended_params": {"energy_multiplier": 0.5}
            })

        if metrics.get("is_flat_contrast"):
            defects.append("Low scene contrast; lacks depth definition.")
            corrections.append({
                "type": "LIGHTING",
                "tool": "setup_light",
                "recommended_params": {"add_rim_light": True}
            })

        is_satisfactory = len(defects) == 0
        return {
            "is_satisfactory": is_satisfactory,
            "defects": defects,
            "corrections": corrections
        }

result_evaluator = ResultEvaluator()
