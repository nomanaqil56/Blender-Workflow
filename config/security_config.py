"""Security Policies, Whitelisting, and Command Validation Rules."""

import os
from pathlib import Path
from typing import Set

AUTH_TOKEN = os.environ.get("BLENDER_AI_AUTH_TOKEN", "blender_ai_studio_local_token_9855")
ALLOWED_HOSTS: Set[str] = {"127.0.0.1", "localhost"}

# Destructive operations requiring explicit user confirmation or flag
DESTRUCTIVE_TOOLS: Set[str] = {
    "delete_object",
    "reset_scene",
    "purge_data",
    "execute_arbitrary_code"
}

# Permitted tools whitelist
PERMITTED_TOOLS: Set[str] = {
    "inspect_scene",
    "inspect_object",
    "create_object",
    "delete_object",
    "select_object",
    "transform_object",
    "duplicate_object",
    "create_mesh",
    "create_truncated_icosahedron",
    "edit_mesh",
    "extrude",
    "inset",
    "bevel",
    "subdivide",
    "add_modifier",
    "configure_modifier",
    "apply_modifier",
    "create_material",
    "assign_material",
    "edit_nodes",
    "setup_camera",
    "setup_light",
    "render_preview",
    "capture_viewport",
    "save_project",
    "export_asset",
    "undo",
    "redo"
}

def is_path_safe(target_path: Path, allowed_root: Path) -> bool:
    """Ensure path traversal does not leave allowed root directories."""
    try:
        resolved = target_path.resolve()
        return str(resolved).startswith(str(allowed_root.resolve()))
    except Exception:
        return False
