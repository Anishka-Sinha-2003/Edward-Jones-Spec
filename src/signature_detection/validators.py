"""Input and output validation functions."""

import re
from typing import List

from .errors import InvalidConfidenceError, InvalidDocumentError, InvalidFieldError
from .models import PDFDocument

__all__ = ["validate_fields_list",
           "validate_pdf_document", "validate_confidence_score"]


def validate_fields_list(fields: List[str]) -> None:
    """Validate that fields list is valid.

    Args:
        fields: List of field names to validate

    Raises:
        InvalidFieldError: If any field is invalid
    """
    if not fields:
        raise InvalidFieldError("Fields list cannot be empty")

    if not isinstance(fields, list):
        raise InvalidFieldError("Fields must be a list")

    for field in fields:
        if not isinstance(field, str):
            raise InvalidFieldError(f"Field must be string, got {type(field)}")

        if not re.match(r"^[a-zA-Z0-9_]+$", field):
            raise InvalidFieldError(
                f"Field '{field}' contains invalid characters. Only alphanumeric and underscore allowed.")

        if len(field) > 100:
            raise InvalidFieldError(
                f"Field '{field}' is too long (max 100 characters)")


def validate_pdf_document(document: PDFDocument) -> None:
    """Validate that a PDF document structure is valid.

    Args:
        document: PDF document to validate

    Raises:
        InvalidDocumentError: If document is invalid
    """
    if not isinstance(document, PDFDocument):
        raise InvalidDocumentError(
            f"Document must be PDFDocument, got {type(document)}")

    if not hasattr(document, "pages"):
        raise InvalidDocumentError("Document must have 'pages' attribute")

    if not isinstance(document.pages, list):
        raise InvalidDocumentError("Document pages must be a list")


def validate_confidence_score(score: float) -> None:
    """Validate that a confidence score is valid.

    Args:
        score: Confidence score to validate

    Raises:
        InvalidConfidenceError: If score is invalid
    """
    if not isinstance(score, (int, float)):
        raise InvalidConfidenceError(
            f"Confidence must be numeric, got {type(score)}")

    if not 0.0 <= score <= 1.0:
        raise InvalidConfidenceError(
            f"Confidence must be between 0.0 and 1.0, got {score}")
