"""Custom exceptions for signature detection."""

__all__ = ["DetectionError", "InvalidFieldError",
           "InvalidDocumentError", "InvalidConfidenceError"]


class DetectionError(Exception):
    """Base exception for detection module."""
    pass


class InvalidFieldError(DetectionError):
    """Raised when a field name is invalid."""
    pass


class InvalidDocumentError(DetectionError):
    """Raised when a document is invalid."""
    pass


class InvalidConfidenceError(DetectionError):
    """Raised when a confidence score is invalid."""
    pass
