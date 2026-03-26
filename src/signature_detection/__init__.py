"""
Signature Detection Module

MVP implementation for detecting signatures and initials in PDF documents.

Exports:
    - DetectionResult: Result dataclass
    - Detector: Abstract base class
    - MockDetector: Mocked implementation
"""

from .models import DetectionResult
from .detector import Detector
from .detectors.mock import MockDetector

__version__ = "0.1.0"
__all__ = ["DetectionResult", "Detector", "MockDetector"]
