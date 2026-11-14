"""
Blender AI Studio - Local AI Server Manager
Monitors port 1234. If LM Studio is running, connects to it.
If not, launches the bundled CUDA-accelerated llama-server on localhost:1234.
"""

import os
import sys
import time
import subprocess
import urllib.request
import urllib.error
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from Core.config import LM_STUDIO_API_URL, LOCAL_MODELS
    from Core.vram_monitor import ResourceMonitor
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from Core.config import LM_STUDIO_API_URL, LOCAL_MODELS
    from Core.vram_monitor import ResourceMonitor

VENDOR_DIR = Path(r"C:\Program Files\LM Studio\resources\app\.webpack\bin\extensions\backends\vendor\win-llama-cuda-vendor-v2")
LLAMA_DIR = Path(r"C:\Program Files\LM Studio\resources\app\.webpack\bin\extensions\backends\llama.cpp-win-x86_64-nvidia-cuda-avx2-2.67.0")
LLAMA_EXE = LLAMA_DIR / "llama-server.exe"


class LocalServerManager:
    """Manages the local inference server (port 1234) using LM Studio or bundled CUDA llama-server."""

    def __init__(self, port: int = 1234):
        self.port = port
        self.api_url = f"http://127.0.0.1:{port}/v1"
        self._process: Optional[subprocess.Popen] = None

    def is_server_running(self) -> bool:
        """Checks if port 1234 responds to /v1/models."""
        try:
            req = urllib.request.Request(f"{self.api_url}/models", headers={"User-Agent": "BlenderAIStudio/1.0"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def start_server(self, model_key: str = "coder", n_gpu_layers: int = 99, ctx_size: int = 4096) -> Dict[str, Any]:
        """Starts local inference server on port 1234 if not already running."""
        if self.is_server_running():
            return {
                "status": "already_running",
                "api_url": self.api_url,
                "message": "Local inference server is already active on port 1234."
            }

        model_path = LOCAL_MODELS.get(model_key)
        if not model_path or not model_path.exists():
            return {
                "status": "error",
                "message": f"Model key '{model_key}' not found on disk: {model_path}"
            }

        # Check VRAM headroom before starting
        vram = ResourceMonitor.get_gpu_status()
        if vram["available"] and vram["free_mb"] < 4500:
            return {
                "status": "warning",
                "message": f"Low VRAM warning: {vram['free_mb']} MB available. Recommended >= 4500 MB for Qwen-7B."
            }

        # Prepare environment with CUDA vendor libraries in PATH
        env = os.environ.copy()
        vendor_path = str(VENDOR_DIR.resolve())
        llama_path = str(LLAMA_DIR.resolve())
        env["PATH"] = f"{vendor_path};{llama_path};" + env.get("PATH", "")

        cmd = [
            str(LLAMA_EXE),
            "-m", str(model_path.resolve()),
            "--port", str(self.port),
            "--host", "127.0.0.1",
            "-ngl", str(n_gpu_layers),
            "-c", str(ctx_size),
            "-fa"
        ]

        # Launch process detached
        try:
            self._process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )

            # Wait for server to become responsive (up to 20 seconds)
            for _ in range(40):
                time.sleep(0.5)
                if self.is_server_running():
                    return {
                        "status": "started",
                        "model": model_key,
                        "model_file": model_path.name,
                        "api_url": self.api_url,
                        "pid": self._process.pid
                    }

            return {
                "status": "timeout",
                "message": "Server started but did not respond to health check within 20s."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def stop_server(self) -> Dict[str, Any]:
        """Stops the managed inference server process."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            return {"status": "stopped", "pid": self._process.pid}
        return {"status": "not_running"}


if __name__ == "__main__":
    mgr = LocalServerManager()
    print("Is server running?", mgr.is_server_running())
