"""Periodic heartbeat monitor for Blender connection health."""

import time
import threading
from typing import Optional
from blender.controller.command_client import CommandClient
from core.event_bus import event_bus
from core.logger import logger

class ConnectionMonitor:
    def __init__(self, client: CommandClient, interval_sec: float = 5.0):
        self.client = client
        self.interval_sec = interval_sec
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._last_state = False

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False

    def _monitor_loop(self):
        while self.is_running:
            connected = self.client.is_connected()
            if connected != self._last_state:
                self._last_state = connected
                event_type = "blender_connected" if connected else "blender_disconnected"
                event_bus.publish(event_type, {"host": self.client.host, "port": self.client.port})
                logger.info(f"Blender connection state changed: {event_type}")
            time.sleep(self.interval_sec)
