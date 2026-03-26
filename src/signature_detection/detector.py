"""Abstract base class for signature detectors."""

from abc import ABC, abstractmethod
from typing import List

from .models import DetectionRequest, DetectionResponse

__all__ = ["Detector"]


class Detector(ABC):
    """Abstract base class for signature/initial detectors.

    Defines the interface for all detector implementations.
    Enables swapping between mock, ML, or other detection strategies.

    Example:
        >>> from signature_detection.detectors.mock import MockDetector
        >>> from signature_detection.models import PDFDocument, PDFPage, DetectionRequest
        >>> 
        >>> detector = MockDetector()
        >>> doc = PDFDocument(pages=[PDFPage(number=1, width=612, height=792)])
        >>> request = DetectionRequest(document=doc, fields=["signature", "initials"])
        >>> response = detector.detect(request)
        >>> print(response.results)
    """

    @abstractmethod
    def detect(self, request: DetectionRequest) -> DetectionResponse:
        """Detect signatures/initials in document.

        Args:
            request: DetectionRequest with document and fields to detect

        Returns:
            DetectionResponse with results and processing time
        """
        pass

    @abstractmethod
    def supports_field(self, field_name: str) -> bool:
        """Check if detector recognizes this field type.

        Args:
            field_name: Field name to check

        Returns:
            True if detector has special handling for this field, False otherwise

        Example:
            >>> detector.supports_field("signature")
            True
            >>> detector.supports_field("unknown_field")
            False
        """
        pass
