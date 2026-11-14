"""Analytical and computer-vision image inspection."""

from pathlib import Path
from typing import Dict, Any
from PIL import Image, ImageStat

class VisualInspector:
    def inspect_image(self, image_path: Path) -> Dict[str, Any]:
        """Compute empirical luminance, contrast, and histogram metrics from rendered frame."""
        if not image_path.exists():
            return {"status": "ERROR", "message": f"Image file not found: {image_path}"}

        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                stat = ImageStat.Stat(img_rgb)

                # Mean RGB and perceived luminance
                mean_r, mean_g, mean_b = stat.mean[:3]
                luminance = (0.299 * mean_r + 0.587 * mean_g + 0.114 * mean_b) / 255.0

                # Standard deviation as contrast metric
                stddev_r, stddev_g, stddev_b = stat.stddev[:3]
                avg_contrast = (stddev_r + stddev_g + stddev_b) / (3.0 * 255.0)

                return {
                    "status": "SUCCESS",
                    "width": img.width,
                    "height": img.height,
                    "avg_luminance": round(luminance, 3),
                    "contrast_score": round(avg_contrast, 3),
                    "is_underexposed": luminance < 0.12,
                    "is_overexposed": luminance > 0.88,
                    "is_flat_contrast": avg_contrast < 0.08
                }
        except Exception as e:
            return {"status": "ERROR", "message": f"Image analysis failed: {e}"}

    def inspect_neural(self, image_path: Path, prompt: str = None) -> Dict[str, Any]:
        """Send base64-encoded render to multimodal model in LM Studio for semantic scene evaluation."""
        import base64
        import io
        from ai.models.lm_studio_client import LMStudioClient
        from ai.models.model_manager import model_manager

        if not image_path.exists():
            return {"available": False, "error": f"Image not found: {image_path}"}

        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                img_rgb.thumbnail((512, 512))
                buf = io.BytesIO()
                img_rgb.save(buf, format="JPEG", quality=85)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            client = LMStudioClient(timeout=90.0)
            if not client.check_health():
                return {"available": False, "reason": "LM Studio offline"}

            p = prompt or "Analyze this 3D render. Describe the geometry, materials, and lighting quality."
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": p},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }]
            active_m = model_manager.discover_active_model()
            res = client.chat_completion(messages=messages, model=active_m, temperature=0.2)
            content = res.get("choices", [{}])[0].get("message", {}).get("content")
            if content:
                return {"available": True, "model": active_m, "analysis": content}
            return {"available": False, "response": res}
        except Exception as e:
            return {"available": False, "error": str(e)}

visual_inspector = VisualInspector()
