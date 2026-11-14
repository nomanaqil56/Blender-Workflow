import os
import sys
from pathlib import Path

# Studio Workspace Roots
PROJECT_ROOT = Path(r"D:\AI Local\Blender AI Studio")
CORE_DIR = PROJECT_ROOT / "Core"
AI_DIR = PROJECT_ROOT / "AI"
BLENDER_DIR = PROJECT_ROOT / "Blender"
GENERATION_DIR = PROJECT_ROOT / "Generation"
ASSETS_DIR = PROJECT_ROOT / "Assets"
PROJECTS_DIR = PROJECT_ROOT / "Projects"
EXPORTS_DIR = PROJECT_ROOT / "Exports"
RENDERS_DIR = PROJECT_ROOT / "Renders"
REPORTS_DIR = PROJECT_ROOT / "Reports"
TESTS_DIR = PROJECT_ROOT / "Tests"
DOCS_DIR = PROJECT_ROOT / "Documentation"

# Subdirectories
INPUT_DIR = GENERATION_DIR / "Input"
OUTPUT_DIR = GENERATION_DIR / "Output"
TEMP_DIR = GENERATION_DIR / "Temporary"
MODELS_DIR = ASSETS_DIR / "Models"
MATERIALS_DIR = ASSETS_DIR / "Materials"
TEXTURES_DIR = ASSETS_DIR / "Textures"
HDRI_DIR = ASSETS_DIR / "HDRI"

# Blender Configuration
BLENDER_LAUNCHER = Path(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\blender-launcher.exe"))
BLENDER_APPX_PATH = Path(r"C:\Program Files\WindowsApps\BlenderFoundation.Blender_5.3.0.0_x64__ppwjx1n5r4v9t\Blender\blender.exe")
BLENDER_USER_SCRIPTS = Path(os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\5.3\scripts"))
BLENDER_USER_CONFIG = Path(os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\5.3\config"))

# Local AI & Model Paths (Discovered on disk)
LM_STUDIO_APP = Path(r"C:\Program Files\LM Studio\LM Studio.exe")
LM_STUDIO_CLI = Path(r"C:\Program Files\LM Studio\resources\app\.webpack\lms.exe")
LM_STUDIO_API_URL = "http://127.0.0.1:1234/v1"

LOCAL_MODELS = {
    "coder": Path(r"D:\AI Local\lmstudio-community\Qwen2.5-Coder-7B-Instruct-GGUF\Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"),
    "vision": Path(r"D:\AI Local\lmstudio-community\Qwen3.5-9B-GGUF\Qwen3.5-9B-Q4_K_M.gguf"),
    "vision_proj": Path(r"D:\AI Local\lmstudio-community\Qwen3.5-9B-GGUF\mmproj-Qwen3.5-9B-BF16.gguf"),
    "reasoning": Path(r"D:\AI Local\lmstudio-community\DeepSeek-R1-0528-Qwen3-8B-GGUF\DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf"),
    "image": Path(r"D:\AI Local\unsloth\Z-Image-Turbo-GGUF\z-image-turbo-Q4_K_M.gguf"),
}

# Network Ports (Strictly Localhost)
BRIDGE_HOST = "127.0.0.1"
BRIDGE_PORT = 9855
MCP_PORT = 9856

# Hardware Budgets (RTX 5060 8GB constraints)
MAX_VRAM_MB = 8151
SAFETY_VRAM_HEADROOM_MB = 1200
MIN_FREE_DISK_GB = 25.0

# Ensure all workspace directories exist
for p in [CORE_DIR, AI_DIR, BLENDER_DIR, GENERATION_DIR, ASSETS_DIR,
          PROJECTS_DIR, EXPORTS_DIR, RENDERS_DIR, REPORTS_DIR, TESTS_DIR, DOCS_DIR,
          INPUT_DIR, OUTPUT_DIR, TEMP_DIR, MODELS_DIR, MATERIALS_DIR, TEXTURES_DIR, HDRI_DIR]:
    p.mkdir(parents=True, exist_ok=True)

