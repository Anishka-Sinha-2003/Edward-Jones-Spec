"""Detector implementations.

This package contains concrete implementations of the Detector interface.
Currently includes MockDetector for MVP testing.
"""

from .mock import MockDetector

__all__ = ["MockDetector"]
