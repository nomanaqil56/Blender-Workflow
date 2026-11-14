"""Thread-safe task queue bridging socket worker threads and Blender main thread."""

import queue
import threading
from typing import Dict, Any, Optional

class QueuedCommand:
    def __init__(self, action: str, params: Dict[str, Any], call_id: str):
        self.action = action
        self.params = params
        self.call_id = call_id
        self.done_event = threading.Event()
        self.result: Optional[Dict[str, Any]] = None

class TaskQueue:
    def __init__(self):
        self._in_queue: queue.Queue = queue.Queue()
        self._active_command: Optional[QueuedCommand] = None

    def enqueue(self, action: str, params: Dict[str, Any], call_id: str) -> QueuedCommand:
        cmd = QueuedCommand(action, params, call_id)
        self._in_queue.put(cmd)
        return cmd

    def get_next(self) -> Optional[QueuedCommand]:
        try:
            return self._in_queue.get_nowait()
        except queue.Empty:
            return None

    def is_empty(self) -> bool:
        return self._in_queue.empty()

task_queue = TaskQueue()
