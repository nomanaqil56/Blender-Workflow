"""Socket server for persistent local IPC with Blender AI Studio."""

import socket
import threading
import json
import time
from typing import Optional
from blender.addon.task_queue import task_queue

class ConnectionManager:
    def __init__(self, host: str = "127.0.0.1", port: int = 9855, auth_token: str = "blender_ai_studio_local_token_9855"):
        self.host = host
        self.port = port
        self.auth_token = auth_token
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.active_connections = 0

    def start(self):
        if self.is_running:
            return

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            self.is_running = True

            self.server_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.server_thread.start()
            print(f"[Blender AI Studio] Socket server listening on {self.host}:{self.port}")
        except Exception as e:
            print(f"[Blender AI Studio] Error starting socket server: {e}")
            self.is_running = False

    def stop(self):
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
        print("[Blender AI Studio] Socket server stopped.")

    def _listen_loop(self):
        while self.is_running:
            try:
                client_sock, addr = self.server_socket.accept()
                self.active_connections += 1
                t = threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"[Blender AI Studio] Accept error: {e}")
                break

    def _handle_client(self, client_sock: socket.socket, addr):
        client_sock.settimeout(60.0)
        buffer = ""
        try:
            while self.is_running:
                data = client_sock.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    response = self._process_request(line)
                    client_sock.sendall((json.dumps(response) + "\n").encode("utf-8"))
        except Exception as e:
            # Client disconnected or timeout
            pass
        finally:
            self.active_connections = max(0, self.active_connections - 1)
            try:
                client_sock.close()
            except Exception:
                pass

    def _process_request(self, raw_json: str) -> dict:
        try:
            req = json.loads(raw_json)
        except Exception as e:
            return {"status": "ERROR", "message": f"Malformed JSON: {e}"}

        # Check authentication
        token = req.get("auth_token", "")
        if token != self.auth_token:
            return {"status": "ERROR", "message": "Authentication failed: invalid auth_token."}

        action = req.get("action", "")
        params = req.get("params", {})
        call_id = req.get("call_id", "unknown")

        if action == "ping":
            return {
                "status": "PONG",
                "session_active": True,
                "server_time": time.time(),
                "call_id": call_id
            }

        # Enqueue for main thread execution
        cmd = task_queue.enqueue(action, params, call_id)

        # Wait for completion event
        finished = cmd.done_event.wait(timeout=55.0)
        if not finished:
            return {
                "status": "ERROR",
                "message": f"Command '{action}' timed out after 55 seconds.",
                "call_id": call_id
            }

        result = cmd.result or {"status": "ERROR", "message": "No result returned"}
        result["call_id"] = call_id
        return result

connection_manager = ConnectionManager()
