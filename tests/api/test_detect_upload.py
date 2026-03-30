"""Integration tests: multipart PDF upload (spec 2603-002)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_detect_upload_success(minimal_pdf_bytes: bytes) -> None:
    files = {"file": ("sample.pdf", minimal_pdf_bytes, "application/pdf")}
    data = {"fields": "signature_field_1,initials"}
    r = client.post("/api/v1/detect", files=files, data=data)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["version"] == "1.0"
    assert "id" in body
    assert "timestamp" in body
    assert "results" in body
    assert isinstance(body["results"], list)
    assert len(body["results"]) == 2
    assert r.headers.get("X-Request-ID")


def test_detect_invalid_pdf_magic() -> None:
    files = {"file": ("bad.pdf", b"not a pdf", "application/pdf")}
    r = client.post("/api/v1/detect", files=files)
    assert r.status_code == 400
    err = r.json()["error"]
    assert err["code"] == "INVALID_PDF_FORMAT"


def test_detect_empty_file() -> None:
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    r = client.post("/api/v1/detect", files=files)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "FILE_REQUIRED"


def test_detect_invalid_field_names(minimal_pdf_bytes: bytes) -> None:
    files = {"file": ("x.pdf", minimal_pdf_bytes, "application/pdf")}
    r = client.post(
        "/api/v1/detect",
        files=files,
        data={"fields": "bad name"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "FIELDS_INVALID"


@patch("api.services.pdf_processing.MAX_FILE_SIZE_BYTES", 100)
def test_detect_file_too_large(minimal_pdf_bytes: bytes) -> None:
    padded = minimal_pdf_bytes + (b"x" * 200)
    files = {"file": ("big.pdf", padded, "application/pdf")}
    r = client.post("/api/v1/detect", files=files)
    assert r.status_code == 413
    assert r.json()["error"]["code"] == "PDF_TOO_LARGE"
