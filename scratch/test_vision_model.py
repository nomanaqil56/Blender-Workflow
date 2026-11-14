import sys
import base64
import io
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.models.model_manager import model_manager
from ai.models.lm_studio_client import LMStudioClient

client = LMStudioClient(timeout=120.0)

test_img_path = PROJECT_ROOT / "Reports" / "TEST_EVIDENCE" / "demo1_football.png"
print(f"Loading {test_img_path}")

with Image.open(test_img_path) as img:
    img = img.convert("RGB")
    img.thumbnail((512, 512))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64_data = base64.b64encode(buf.getvalue()).decode("utf-8")

print(f"Resized image b64 len: {len(b64_data)}")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What 3D model is shown in this image? Describe its geometry, panels, and lighting briefly in 2 sentences."},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64_data}"
                }
            }
        ]
    }
]

resp = client.chat_completion(
    messages=messages,
    model="qwen/qwen3.5-9b",
    temperature=0.2
)

choice = resp.get("choices", [{}])[0].get("message", {})
content = choice.get("content", "")
print("VISION MODEL OUTPUT:\n", content)
