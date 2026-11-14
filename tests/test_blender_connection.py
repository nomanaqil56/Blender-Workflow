"""Test Suite: Blender Persistent Connection and Authentication."""

import unittest
from blender.controller.blender_controller import BlenderController
from blender.controller.command_client import CommandClient
from config.blender_config import BLENDER_HOST, BLENDER_PORT

class TestBlenderConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = BlenderController(host=BLENDER_HOST, port=BLENDER_PORT)

    @classmethod
    def tearDownClass(cls):
        cls.controller.disconnect()

    def test_01_connection_and_ping(self):
        """Verify socket connects and responds to ping."""
        connected = self.controller.connect()
        self.assertTrue(connected, "Failed to connect to Blender socket server.")
        ping_res = self.controller.ping()
        self.assertEqual(ping_res.get("status"), "PONG")
        self.assertTrue(ping_res.get("session_active"))

    def test_02_authentication_rejection(self):
        """Verify connection with invalid auth token is rejected."""
        unauth_client = CommandClient(host=BLENDER_HOST, port=BLENDER_PORT, auth_token="INVALID_TOKEN_999")
        try:
            res = unauth_client.send_command("inspect_scene", {})
            self.assertEqual(res.get("status"), "ERROR")
            self.assertIn("Authentication failed", res.get("message", ""))
        finally:
            unauth_client.disconnect()

    def test_03_scene_inspection(self):
        """Verify scene can be inspected over socket."""
        res = self.controller.inspect_scene(detailed=True)
        self.assertEqual(res.get("status"), "SUCCESS")
        self.assertIn("total_objects", res)
        self.assertIn("objects", res)

if __name__ == "__main__":
    unittest.main()
