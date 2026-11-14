"""Decoupled Event Bus for system-wide notifications and logging."""

from typing import Callable, Dict, List, Any
import threading

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[str, Any], None]]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, callback: Callable[[str, Any], None]):
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[str, Any], None]):
        with self._lock:
            if event_type in self._listeners and callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)

    def publish(self, event_type: str, data: Any = None):
        callbacks = []
        with self._lock:
            if event_type in self._listeners:
                callbacks.extend(self._listeners[event_type])
            if "*" in self._listeners:
                callbacks.extend(self._listeners["*"])

        for cb in callbacks:
            try:
                cb(event_type, data)
            except Exception as e:
                print(f"[EventBus Error in {cb.__name__}]: {e}")

# Global instance
event_bus = EventBus()
