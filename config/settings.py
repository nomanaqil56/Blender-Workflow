"""Global Application Settings for Blender AI Studio.
Provides unified configuration, directory paths, and runtime flags.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Root Project Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Core Directories
ASSETS_DIR = PROJECT_ROOT / "Assets"
PROJECTS_DIR = PROJECT_ROOT / "Projects"
EXPORTS_DIR = PROJECT_ROOT / "Exports"
RENDERS_DIR = PROJECT_ROOT / "Renders"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "reports" / "logs"

# Ensure directories exist
for directory in [ASSETS_DIR, PROJECTS_DIR, EXPORTS_DIR, RENDERS_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Hardware Profile (NVIDIA RTX 5060 Laptop GPU - 8GB VRAM)
HARDWARE_PROFILE = {
    "gpu_name": "NVIDIA GeForce RTX 5060 Laptop GPU",
    "total_vram_gb": 8.0,
    "safe_vram_margin_gb": 6.8,
    "system_ram_gb": 24.0,
    "cpu_model": "Intel Core i7-14650HX",
    "os": "Windows 11"
}

# Runtime Limits
MAX_TASK_DURATION_SEC = 300
MAX_CORRECTION_ITERATIONS = 5
MAX_TOOL_CALLS_PER_TASK = 50
MAX_REQUEST_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_TIMEOUT_SEC = 45

# Version Info
APP_NAME = "Blender AI Studio"
APP_VERSION = "2.0.0"
API_VERSION = "1.0"
