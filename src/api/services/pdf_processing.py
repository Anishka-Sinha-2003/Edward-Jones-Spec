"""PDF upload validation and parsing into core PDFDocument models."""

from __future__ import annotations

import logging
from io import BytesIO
from typing import Optional, Tuple

import pdfplumber

from api.exceptions import PDFParsingError, PDFValidationError, FileTooLargeError
from signature_detection.models import PDFDocument, PDFObject, PDFPage

logger = logging.getLogger(__name__)

# Spec 2603-002: max 50MB
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
PDF_MAGIC = b"%PDF"


class PDFProcessingService:
    """Validate uploads and parse PDF bytes into PDFDocument."""

    def __init__(self) -> None:
        self._logger = logger

    def validate_bytes(
        self,
        data: bytes,
        _content_type: Optional[str],
        filename: Optional[str],
    ) -> None:
        """Validate size and PDF magic bytes (Content-Type varies by client)."""
        if not data:
            raise PDFValidationError(
                "FILE_REQUIRED",
                "No file content provided",
                400,
            )

        if len(data) > MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError()

        # Magic bytes are authoritative (browsers vary Content-Type)
        if not data.startswith(PDF_MAGIC):
            raise PDFValidationError(
                "INVALID_PDF_FORMAT",
                "File is not a valid PDF document",
                400,
            )

        if filename and not filename.lower().endswith(".pdf"):
            self._logger.warning("Upload filename does not end with .pdf: %s", filename)

    def parse_pdf_bytes(self, data: bytes, filename: str) -> PDFDocument:
        """Parse PDF bytes into PDFDocument using pdfplumber."""
        try:
            with pdfplumber.open(BytesIO(data)) as pdf:
                pages: list[PDFPage] = []
                for i, page in enumerate(pdf.pages, start=1):
                    w = float(page.width)
                    h = float(page.height)
                    objs: list[PDFObject] = []
                    text = page.extract_text()
                    if text and text.strip():
                        objs.append(
                            PDFObject(
                                obj_type="text",
                                x=0.0,
                                y=0.0,
                                width=w,
                                height=h,
                                content=text[:8000],
                            )
                        )
                    pages.append(
                        PDFPage(number=i, width=w, height=h, objects=objs)
                    )
                return PDFDocument(
                    pages=pages,
                    metadata={
                        "name": filename,
                        "pages": len(pages),
                    },
                )
        except Exception as e:
            self._logger.exception("PDF parsing failed")
            raise PDFParsingError(f"Could not parse PDF: {e}") from e


def validate_pdf_upload(
    data: bytes,
    content_type: Optional[str],
    filename: Optional[str],
) -> Tuple[bool, Optional[str]]:
    """Legacy tuple-style validation for tests (optional)."""
    try:
        PDFProcessingService().validate_bytes(data, content_type, filename)
        return True, None
    except (PDFValidationError, FileTooLargeError) as e:
        return False, e.message
