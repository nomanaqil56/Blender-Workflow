"""TCP Socket client communicating with the Blender addon."""

import socket
import json
import time
from typing import Dict, Any, Optional
from config.blender_config import BLENDER_HOST, BLENDER_PORT, SOCKET_TIMEOUT, COMMAND_TIMEOUT
from config.security_config import AUTH_TOKEN
from core.logger import logger

class CommandClient:
    def __init__(self, host: str = BLENDER_HOST, port: int = BLENDER_PORT, auth_token: str = AUTH_TOKEN):
        self.host = host
        self.port = port
        self.auth_token = auth_token
        self._sock: Optional[socket.socket] = None

    def connect(self, timeout: float = SOCKET_TIMEOUT) -> bool:
        """Establish connection to Blender socket server."""
        self.disconnect()
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(timeout)
            self._sock.connect((self.host, self.port))
            return True
        except Exception as e:
            logger.debug(f"Connection to Blender at {self.host}:{self.port} failed: {e}")
            self._sock = None
            return False

    def is_connected(self) -> bool:
        if not self._sock:
            return False
        try:
            # Quick ping test
            res = self.send_command("ping", {})
            return res.get("status") == "PONG"
        except Exception:
            self.disconnect()
            return False

    def disconnect(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def send_command(self, action: str, params: Dict[str, Any] = None, timeout: float = COMMAND_TIMEOUT) -> Dict[str, Any]:
        """Send JSON command and wait for response."""
        if not self._sock:
            if not self.connect():
                return {"status": "ERROR", "message": f"Could not connect to Blender at {self.host}:{self.port}."}

        payload = {
            "auth_token": self.auth_token,
            "action": action,
            "params": params or {},
            "call_id": f"call_{int(time.time()*1000)}"
        }

        try:
            self._sock.settimeout(timeout)
            message = (json.dumps(payload) + "\n").encode("utf-8")
            self._sock.sendall(message)

            # Receive newline-delimited response
            buffer = ""
            while "\n" not in buffer:
                chunk = self._sock.recv(4096)
                if not chunk:
                    raise ConnectionResetError("Connection closed by Blender server.")
                buffer += chunk.decode("utf-8")

            line = buffer.split("\n", 1)[0].strip()
            return json.loads(line)
        except Exception as e:
            logger.error(f"Command '{action}' failed: {e}")
            self.disconnect()
            return {"status": "ERROR", "message": str(e)}
