"""Streaming handler for chunked token delivery."""

from typing import Generator, Dict, Any
import json
import requests

def stream_chat_response(url: str, payload: Dict[str, Any]) -> Generator[str, None, None]:
    """Stream token deltas from OpenAI-compatible SSE endpoint."""
    payload["stream"] = True
    try:
        with requests.post(url, json=payload, stream=True, timeout=30) as r:
            for line in r.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8")
                if decoded.startswith("data: "):
                    content = decoded[6:].strip()
                    if content == "[DONE]":
                        break
                    try:
                        data = json.loads(content)
                        delta = data["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue
    except Exception as e:
        yield f"[Streaming error: {e}]"
