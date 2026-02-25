"""
ESPx Innovations Engine
=======================
Maps user-described firmware intentions to ESP32 capabilities,
firmware templates, and configuration recommendations.
"""

from .engine import InnovationsEngine
from .knowledge_base import FIRMWARE_KNOWLEDGE_BASE

__all__ = ["InnovationsEngine", "FIRMWARE_KNOWLEDGE_BASE"]
__version__ = "1.0.0"
