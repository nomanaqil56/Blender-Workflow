"""Structured Logging System for Blender AI Studio."""

import logging
import sys
from pathlib import Path
from config.settings import LOGS_DIR

def get_logger(name: str = "BlenderAIStudio") -> logging.Logger:
    """Return a configured logger with console and file handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.INFO)
    c_handler.setFormatter(formatter)
    logger.addHandler(c_handler)

    # File Handler
    log_file = LOGS_DIR / "blender_ai_studio.log"
    try:
        f_handler = logging.FileHandler(log_file, encoding="utf-8")
        f_handler.setLevel(logging.DEBUG)
        f_handler.setFormatter(formatter)
        logger.addHandler(f_handler)
    except Exception as e:
        print(f"Warning: Could not initialize log file: {e}")

    return logger

logger = get_logger()
