import shutil
import subprocess
import json
from typing import Dict, Any, Optional

try:
    from Core.config import MAX_VRAM_MB, SAFETY_VRAM_HEADROOM_MB, MIN_FREE_DISK_GB, PROJECT_ROOT
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from Core.config import MAX_VRAM_MB, SAFETY_VRAM_HEADROOM_MB, MIN_FREE_DISK_GB, PROJECT_ROOT


class ResourceMonitor:
    """Monitors system GPU VRAM, host RAM, and storage headroom."""

    @staticmethod
    def get_gpu_status() -> Dict[str, Any]:
        """Queries nvidia-smi for real-time GPU VRAM and utilization."""
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            line = result.stdout.strip().split("\n")[0]
            parts = [p.strip() for p in line.split(",")]
            
            return {
                "available": True,
                "name": parts[0],
                "total_mb": float(parts[1]),
                "used_mb": float(parts[2]),
                "free_mb": float(parts[3]),
                "utilization_pct": float(parts[4]),
                "temp_c": float(parts[5]),
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "total_mb": MAX_VRAM_MB,
                "used_mb": 0.0,
                "free_mb": MAX_VRAM_MB,
                "utilization_pct": 0.0,
                "temp_c": 0.0
            }

    @staticmethod
    def get_disk_status(drive_path: str = "D:\\") -> Dict[str, Any]:
        """Checks free disk space against the 25GB studio threshold."""
        try:
            total, used, free = shutil.disk_usage(drive_path)
            free_gb = free / (1024 ** 3)
            total_gb = total / (1024 ** 3)
            used_gb = used / (1024 ** 3)
            return {
                "drive": drive_path,
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "healthy": free_gb >= MIN_FREE_DISK_GB
            }
        except Exception as e:
            return {"drive": drive_path, "healthy": True, "error": str(e)}

    @classmethod
    def can_allocate_vram(cls, requested_mb: float) -> bool:
        """Determines if requested VRAM fits within the 8GB budget with safety headroom."""
        gpu = cls.get_gpu_status()
        if not gpu["available"]:
            return True  # Fallback if no nvidia-smi
        usable_free = gpu["free_mb"] - SAFETY_VRAM_HEADROOM_MB
        return usable_free >= requested_mb

    @classmethod
    def get_system_summary(cls) -> Dict[str, Any]:
        """Provides complete health status for QA and logging."""
        gpu = cls.get_gpu_status()
        disk = cls.get_disk_status("D:\\")
        return {
            "gpu": gpu,
            "disk": disk,
            "can_run_generation": cls.can_allocate_vram(4000),  # e.g. 4GB generation model
            "can_run_cycles": cls.can_allocate_vram(2500),      # e.g. 2.5GB render scene
        }


if __name__ == "__main__":
    summary = ResourceMonitor.get_system_summary()
    print(json.dumps(summary, indent=2))

