"""
Blender AI Studio - Provider Abstraction Layer
Defines clean interfaces for Local and Cloud AI engines with
strict privacy and local-first fallback mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseProvider(ABC):
    """Base class for all Studio AI providers."""

    def __init__(self, name: str, is_cloud: bool = False):
        self.name = name
        self.is_cloud = is_cloud

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if provider has active credentials or running service."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Returns provider connectivity and resource diagnostic report."""
        pass


class BaseLLMProvider(BaseProvider):
    """Interface for text, code, and vision generation."""

    @abstractmethod
    def generate_bpy_code(self, prompt: str, category: str = "general") -> Dict[str, Any]:
        pass

    @abstractmethod
    def inspect_visuals(self, image_path: str, prompt: str) -> Dict[str, Any]:
        pass


class Base3DProvider(BaseProvider):
    """Interface for 3D mesh generation backends."""

    @abstractmethod
    def generate_mesh(self, prompt: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        pass

