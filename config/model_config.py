"""AI Model Configuration and Local LLM Endpoint Settings."""

from pathlib import Path
from typing import Dict, Any

LM_STUDIO_API_URL = "http://127.0.0.1:1234/v1"
MODELS_ROOT = Path(r"D:\AI Local")

LOCAL_MODELS = {
    "coder": {
        "id": "qwen2.5-coder-7b-instruct",
        "name": "Qwen2.5-Coder-7B-Instruct",
        "path": MODELS_ROOT / "lmstudio-community" / "Qwen2.5-Coder-7B-Instruct-GGUF" / "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf",
        "context_length": 8192,
        "role": "Tool calling, code generation, parameter synthesis",
        "vram_estimate_gb": 4.8
    },
    "reasoning": {
        "id": "deepseek-r1-0528-qwen3-8b",
        "name": "DeepSeek-R1-Qwen3-8B",
        "path": MODELS_ROOT / "lmstudio-community" / "DeepSeek-R1-0528-Qwen3-8B-GGUF" / "DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf",
        "context_length": 8192,
        "role": "Complex multi-step task planning, spatial reasoning",
        "vram_estimate_gb": 5.2
    },
    "vision": {
        "id": "qwen3.5-9b",
        "name": "Qwen3.5-9B-Vision",
        "path": MODELS_ROOT / "lmstudio-community" / "Qwen3.5-9B-GGUF" / "Qwen3.5-9B-Q4_K_M.gguf",
        "mmproj_path": MODELS_ROOT / "lmstudio-community" / "Qwen3.5-9B-GGUF" / "mmproj-Qwen3.5-9B-BF16.gguf",
        "context_length": 4096,
        "role": "Visual inspection, quality check, render evaluation",
        "vram_estimate_gb": 6.2
    },
    "image_synth": {
        "id": "z-image-turbo",
        "name": "Z-Image-Turbo",
        "path": MODELS_ROOT / "unsloth" / "Z-Image-Turbo-GGUF" / "z-image-turbo-Q4_K_M.gguf",
        "role": "Texture synthesis, concept generation",
        "vram_estimate_gb": 4.0
    }
}

LLAMA_SERVER_EXECUTABLE = Path(r"C:\Users\noman\.lmstudio\extensions\backends\llama.cpp-win-x86_64-nvidia-cuda12-avx2-2.70.0\llama-server.exe")
