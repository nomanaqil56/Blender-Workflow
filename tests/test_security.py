"""Test Suite: Security Policies, Permissions, and Input Validation."""

import unittest
from pathlib import Path
from config.security_config import is_path_safe, AUTH_TOKEN, DESTRUCTIVE_TOOLS
from core.permission_manager import PermissionManager
from config.settings import PROJECT_ROOT

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.pm = PermissionManager()

    def test_01_path_traversal_guard(self):
        """Verify is_path_safe prevents directory traversal outside project root."""
        safe_path = PROJECT_ROOT / "Exports" / "model.glb"
        unsafe_path = PROJECT_ROOT / ".." / "Windows" / "System32" / "calc.exe"

        self.assertTrue(is_path_safe(safe_path, PROJECT_ROOT))
        self.assertFalse(is_path_safe(unsafe_path, PROJECT_ROOT))

    def test_02_destructive_tool_guard(self):
        """Verify destructive operations require explicit confirmation."""
        permitted, reason = self.pm.check_tool_permission("delete_object", {"object_name": "Cube", "confirm": False})
        self.assertFalse(permitted)
        self.assertIn("confirm=True", reason)

        permitted_ok, reason_ok = self.pm.check_tool_permission("delete_object", {"object_name": "Cube", "confirm": True})
        self.assertTrue(permitted_ok)

    def test_03_whitelist_guard(self):
        """Verify unregistered or dangerous tools are rejected."""
        permitted, reason = self.pm.check_tool_permission("execute_malicious_script", {})
        self.assertFalse(permitted)
        self.assertIn("whitelist", reason)

if __name__ == "__main__":
    unittest.main()
