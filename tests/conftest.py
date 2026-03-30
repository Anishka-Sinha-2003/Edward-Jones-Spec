"""Shared pytest fixtures."""

from io import BytesIO

import pytest
from pypdf import PdfWriter


@pytest.fixture
def minimal_pdf_bytes() -> bytes:
    """Single blank page PDF for integration tests."""
    w = PdfWriter()
    w.add_blank_page(width=612, height=792)
    buf = BytesIO()
    w.write(buf)
    return buf.getvalue()
