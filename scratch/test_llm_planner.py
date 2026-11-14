import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.models.model_manager import model_manager
from core.tool_registry import tool_registry

active = model_manager.discover_active_model()
print(f"Active Model: {active}")

tools = tool_registry.list_tools()
tool_docs = "\n".join([f"- {t.name}: {t.description}. Parameters: {list(t.parameters_schema.get('properties', {}).keys())}" for t in tools])

system_prompt = f"""You are Blender AI Studio, an autonomous 3D agent controlling desktop Blender.
Your job is to decompose the user request into an ordered sequence of executable tool steps.
You MUST reply with a valid JSON array of step objects inside a ```json ``` block:
```json
[
  {{
    "step_index": 1,
    "description": "Short explanation",
    "tool_name": "tool_name_here",
    "parameters": {{"param1": "val1"}}
  }}
]
```

Available Tools:
{tool_docs}
"""

user_msg = "Create a realistic football with studio lighting, camera, and render an image."

resp = model_manager.client.chat_completion(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg}
    ],
    model=active,
    temperature=0.0
)

choice = resp.get("choices", [{}])[0].get("message", {})
content = choice.get("content", "")
reasoning = choice.get("reasoning_content", "")
print("REASONING LENGTH:", len(reasoning))
print("LLM RESPONSE CONTENT:")
print(content)
