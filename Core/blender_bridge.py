"""
Blender AI Studio - Host Bridge Client
Provides seamless high-level Python API to control Blender either via
persistent localhost socket bridge (when Blender GUI is open) or via
headless execution fallback (blender-launcher.exe -b).
"""

import sys
import os
import json
import socket
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from Core.config import (
        BRIDGE_HOST, BRIDGE_PORT, BLENDER_LAUNCHER,
        PROJECT_ROOT, TEMP_DIR, PROJECTS_DIR, RENDERS_DIR, EXPORTS_DIR
    )
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from Core.config import (
        BRIDGE_HOST, BRIDGE_PORT, BLENDER_LAUNCHER,
        PROJECT_ROOT, TEMP_DIR, PROJECTS_DIR, RENDERS_DIR, EXPORTS_DIR
    )

BLENDER_SERVER_SCRIPT = PROJECT_ROOT / "Blender" / "Scripts" / "blender_server.py"


class BlenderBridge:
    """Bi-directional RPC bridge connecting Antigravity to Blender."""

    def __init__(self, host: str = BRIDGE_HOST, port: int = BRIDGE_PORT,
                 blend_file: Optional[str] = None):
        self.host = host
        self.port = port
        self.session_file = Path(blend_file) if blend_file else (PROJECTS_DIR / "_active_session.blend")

    def new_session(self) -> None:
        """Resets the active session blend file so next command starts from a clean scene."""
        if self.session_file.exists():
            try:
                self.session_file.unlink()
            except Exception as e:
                print(f"[BlenderBridge] Could not delete old session: {e}")

    def is_socket_alive(self) -> bool:
        """Checks if Blender's background socket server is actively listening."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((self.host, self.port))
            s.close()
            return True
        except (socket.error, ConnectionRefusedError, socket.timeout):
            return False

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dispatches request via live socket or headless execution."""
        payload = {"method": method, "params": params or {}}

        # Attempt 1: Live Socket
        if self.is_socket_alive():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(120.0)  # Extended timeout for heavy renders
                s.connect((self.host, self.port))
                req_bytes = (json.dumps(payload) + "\n").encode("utf-8")
                s.sendall(req_bytes)

                data = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if b"\n" in chunk:
                        break
                s.close()
                if data:
                    return json.loads(data.decode("utf-8").strip())
            except Exception as e:
                print(f"[BlenderBridge] Socket dispatch failed ({e}), falling back to headless runner.")

        # Attempt 2: Headless CLI Fallback
        return self._run_headless(payload)

    def _run_headless(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes operation via headless Blender background process."""
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        req_path = TEMP_DIR / f"req_{int(time.time() * 1000)}.json"
        resp_path = TEMP_DIR / f"resp_{int(time.time() * 1000)}.json"

        try:
            with open(req_path, "w", encoding="utf-8") as f:
                json.dump(payload, f)

            cmd = [str(BLENDER_LAUNCHER), "-b"]
            if self.session_file.exists():
                cmd.extend([str(self.session_file)])

            cmd.extend([
                "--python", str(BLENDER_SERVER_SCRIPT),
                "--", "--exec-json", str(req_path), str(resp_path),
                "--save-session", str(self.session_file)
            ])

            # Run Blender
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if os.path.isfile(resp_path):
                with open(resp_path, "r", encoding="utf-8") as f:
                    resp = json.load(f)
                return resp
            else:
                return {
                    "status": "error",
                    "message": "Headless Blender finished without producing response.",
                    "stderr": res.stderr,
                    "stdout": res.stdout
                }
        finally:
            # Cleanup temp json files
            if req_path.exists():
                try: req_path.unlink()
                except: pass
            if resp_path.exists():
                try: resp_path.unlink()
                except: pass

    # High-level API convenience wrappers

    def inspect_scene(self) -> Dict[str, Any]:
        return self.send_request("inspect_scene")

    def create_object(self, obj_type: str = "cube", name: Optional[str] = None,
                      location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1),
                      size: float = 2.0, **kwargs) -> Dict[str, Any]:
        params = {
            "obj_type": obj_type,
            "name": name,
            "location": list(location),
            "rotation": list(rotation),
            "scale": list(scale),
            "size": size,
            **kwargs
        }
        return self.send_request("create_object", params)

    def modify_object(self, name: str, location=None, rotation=None, scale=None,
                      visible: Optional[bool] = None, select: Optional[bool] = None,
                      apply_transforms: bool = False) -> Dict[str, Any]:
        params = {"name": name, "apply_transforms": apply_transforms}
        if location is not None: params["location"] = list(location)
        if rotation is not None: params["rotation"] = list(rotation)
        if scale is not None: params["scale"] = list(scale)
        if visible is not None: params["visible"] = visible
        if select is not None: params["select"] = select
        return self.send_request("modify_object", params)

    def mesh_operations(self, name: str, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.send_request("mesh_operations", {"name": name, "action": action, "params": params or {}})

    def create_material(self, name: str, pbr_properties: Optional[Dict[str, Any]] = None,
                        assign_to: Optional[str] = None) -> Dict[str, Any]:
        return self.send_request("create_material", {
            "name": name,
            "pbr_properties": pbr_properties or {},
            "assign_to": assign_to
        })

    def assign_texture(self, material_name: str, texture_type: str, image_path: str) -> Dict[str, Any]:
        return self.send_request("assign_texture", {
            "material_name": material_name,
            "texture_type": texture_type,
            "image_path": str(Path(image_path).resolve())
        })

    def setup_lighting(self, light_type: str = "SUN", energy: float = 3.0,
                       color=(1.0, 1.0, 1.0), location=(5.0, -5.0, 8.0),
                       rotation=(45.0, 0.0, 45.0), name: str = "StudioLight") -> Dict[str, Any]:
        return self.send_request("setup_lighting", {
            "light_type": light_type,
            "energy": energy,
            "color": list(color),
            "location": list(location),
            "rotation": list(rotation),
            "name": name
        })

    def setup_camera(self, location=(7.0, -7.0, 5.0), rotation=(60.0, 0.0, 45.0),
                     focal_length: float = 50.0, look_at: Optional[tuple] = None,
                     name: str = "Camera") -> Dict[str, Any]:
        params = {
            "location": list(location),
            "rotation": list(rotation),
            "focal_length": focal_length,
            "name": name
        }
        if look_at is not None:
            params["look_at"] = list(look_at)
        return self.send_request("setup_camera", params)

    def apply_geometry_nodes(self, object_name: str, node_graph_type: str = "wireframe",
                             params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.send_request("apply_geometry_nodes", {
            "object_name": object_name,
            "node_graph_type": node_graph_type,
            "params": params or {}
        })

    def render(self, output_path: str, engine: str = "CYCLES", resolution_x: int = 1280,
               resolution_y: int = 720, samples: int = 64, device: str = "GPU") -> Dict[str, Any]:
        return self.send_request("render", {
            "output_path": str(Path(output_path).resolve()),
            "engine": engine,
            "resolution_x": resolution_x,
            "resolution_y": resolution_y,
            "samples": samples,
            "device": device
        })

    def inspect_render(self, image_path: str) -> Dict[str, Any]:
        return self.send_request("inspect_render", {"image_path": str(Path(image_path).resolve())})

    def save_project(self, filepath: str) -> Dict[str, Any]:
        return self.send_request("save_project", {"filepath": str(Path(filepath).resolve())})

    def import_asset(self, filepath: str, format: Optional[str] = None) -> Dict[str, Any]:
        return self.send_request("import_asset", {
            "filepath": str(Path(filepath).resolve()),
            "format": format
        })

    def export_asset(self, filepath: str, format: Optional[str] = None,
                     selected_only: bool = False) -> Dict[str, Any]:
        return self.send_request("export_asset", {
            "filepath": str(Path(filepath).resolve()),
            "format": format,
            "selected_only": selected_only
        })

    def execute_script(self, code: str) -> Dict[str, Any]:
        return self.send_request("execute_script", {"code": code})
