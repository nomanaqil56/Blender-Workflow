"""
Blender AI Studio - Multimodal Vision & Render Quality Inspector
Inspects reference images, rendered frames, and geometry silhouettes
using PIL heuristics and local Qwen3.5-9B vision adapter.
"""

import os
import sys
import json
import base64
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from PIL import Image, ImageStat
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from Core.config import LM_STUDIO_API_URL, LOCAL_MODELS
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from Core.config import LM_STUDIO_API_URL, LOCAL_MODELS


class VisionInspector:
    """Inspects reference images and render outputs."""

    def __init__(self, api_url: str = LM_STUDIO_API_URL):
        self.api_url = api_url.rstrip("/")

    @staticmethod
    def encode_image_base64(image_path: str) -> str:
        """Converts an image file to a base64 data URI."""
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext = Path(image_path).suffix.lstrip(".").lower()
        mime = f"image/{ext}" if ext in ["png", "jpeg", "jpg", "webp"] else "image/png"
        return f"data:{mime};base64,{encoded}"

    @staticmethod
    def analyze_heuristics(image_path: str) -> Dict[str, Any]:
        """Performs fast heuristic visual inspection using Pillow."""
        if not os.path.isfile(image_path):
            return {"valid": False, "error": f"File not found: {image_path}"}

        if not HAS_PIL:
            return {"valid": True, "warning": "PIL not installed, skipped heuristic metrics."}

        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode

                # Convert to grayscale for luminance statistics
                gray = img.convert("L")
                stat = ImageStat.Stat(gray)
                mean_lum = stat.mean[0]
                stddev_lum = stat.stddev[0]
                rms = stat.rms[0]

                # Determine if image is entirely blank / pitch black / blown out
                is_blank = mean_lum < 1.0 or mean_lum > 254.0
                has_good_contrast = stddev_lum > 15.0

                return {
                    "valid": True,
                    "resolution": [width, height],
                    "aspect_ratio": round(width / max(1, height), 3),
                    "format": format_name,
                    "mode": mode,
                    "mean_luminance": round(mean_lum, 2),
                    "contrast_stddev": round(stddev_lum, 2),
                    "is_blank": is_blank,
                    "has_good_contrast": has_good_contrast,
                    "quality_rating": "PASS" if (not is_blank and has_good_contrast) else "NEEDS_ADJUSTMENT"
                }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def inspect_with_vision_llm(self, image_path: str, prompt: str = "Evaluate this 3D render quality and composition.") -> Dict[str, Any]:
        """Sends image to local Qwen3.5-9B vision endpoint if server is available."""
        heuristics = self.analyze_heuristics(image_path)
        if not heuristics.get("valid"):
            return heuristics

        b64_url = self.encode_image_base64(image_path)
        payload = {
            "model": "qwen3.5-9b",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": b64_url}}
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0.2
        }

        try:
            url = f"{self.api_url}/chat/completions"
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json", "User-Agent": "BlenderAIStudio/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                commentary = res["choices"][0]["message"]["content"]
                return {
                    "heuristics": heuristics,
                    "vision_ai_commentary": commentary,
                    "ai_analyzed": True
                }
        except Exception as e:
            return {
                "heuristics": heuristics,
                "ai_analyzed": False,
                "note": f"Local vision LLM not available ({e}); using heuristic inspection."
            }


if __name__ == "__main__":
    inspector = VisionInspector()
    test_render = Path(r"D:\AI Local\Blender AI Studio\Renders\phase2_render.png")
    if test_render.exists():
        report = inspector.analyze_heuristics(str(test_render))
        print(json.dumps(report, indent=2))
    else:
        print("No test render to inspect.")

