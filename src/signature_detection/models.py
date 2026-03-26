"""Data models for signature detection."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

__all__ = ["DetectionResult", "PDFObject", "PDFPage",
           "PDFDocument", "DetectionRequest", "DetectionResponse"]


@dataclass
class DetectionResult:
    """Result of detecting a signature or initial field.

    Attributes:
        field_name: Name of the field (e.g., "signature_field_1")
        status: Detection status ("present", "absent", or "uncertain")
        confidence: Confidence score between 0.0 and 1.0
        metadata: Additional context (position, size, etc.)
    """
    field_name: str
    status: Literal["present", "absent", "uncertain"]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate confidence is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.status not in ("present", "absent", "uncertain"):
            raise ValueError(
                f"Status must be 'present', 'absent', or 'uncertain', got {self.status}")


@dataclass
class PDFObject:
    """Represents an object in a PDF page.

    Attributes:
        obj_type: Type of object ("text", "image", "shape", "path")
        x: X coordinate (top-left)
        y: Y coordinate (top-left)
        width: Object width
        height: Object height
        content: Content (text string or image data)
    """
    obj_type: Literal["text", "image", "shape", "path"]
    x: float
    y: float
    width: float
    height: float
    content: Any = None


@dataclass
class PDFPage:
    """Represents a page in a PDF document.

    Attributes:
        number: Page number (1-indexed)
        width: Page width
        height: Page height
        objects: List of objects on this page
    """
    number: int
    width: float
    height: float
    objects: List[PDFObject] = field(default_factory=list)


@dataclass
class PDFDocument:
    """Represents a parsed PDF document.

    Attributes:
        pages: List of pages in document
        metadata: Document-level metadata
    """
    pages: List[PDFPage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectionRequest:
    """Request to detect signatures in a document.

    Attributes:
        document: Parsed PDF document
        fields: Field names to detect
    """
    document: PDFDocument
    fields: List[str]


@dataclass
class DetectionResponse:
    """Response from detection operation.

    Attributes:
        results: List of detection results
        processing_time_ms: Time taken for detection in milliseconds
    """
    results: List[DetectionResult]
    processing_time_ms: int = 0
