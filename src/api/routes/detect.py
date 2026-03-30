"""
Detection endpoint — POST /api/v1/detect (multipart PDF).

Spec 2603-002: file upload + optional fields; JSON response with request id.
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, File, Form, Request, UploadFile

from api.exceptions import APIError, DetectionTimeoutError, DetectorRuntimeError
from api.exceptions import PDFParsingError, PDFValidationError
from api.schemas.responses import DetectionResponseData
from api.services.detector_service import DetectorService
from api.services.pdf_processing import PDFProcessingService
from signature_detection.detectors.mock import MockDetector

logger = logging.getLogger(__name__)

router = APIRouter()

_detector = MockDetector()
_detector_service = DetectorService(_detector)
_pdf_service = PDFProcessingService()

DETECT_TIMEOUT_S = 5.0
FIELD_NAME_RE = re.compile(r"^[a-zA-Z0-9_]+$")


def _default_fields() -> List[str]:
    return ["signature", "initials"]


def _parse_fields_param(raw: Optional[str]) -> List[str]:
    if raw is None or not str(raw).strip():
        return _default_fields()
    parts = [p.strip() for p in str(raw).split(",") if p.strip()]
    return parts if parts else _default_fields()


def _validate_field_names(names: List[str]) -> None:
    for n in names:
        if not FIELD_NAME_RE.match(n):
            raise PDFValidationError(
                "FIELDS_INVALID",
                f"Field names must be alphanumeric with underscores: invalid {n!r}",
            )


async def _detect_with_timeout(document, field_list: List[str]):
    loop = asyncio.get_running_loop()
    return await asyncio.wait_for(
        loop.run_in_executor(
            None,
            lambda: _detector_service.detect_fields(document, field_list),
        ),
        timeout=DETECT_TIMEOUT_S,
    )


@router.post(
    "/api/v1/detect",
    summary="Detect signatures in a PDF",
    description=(
        "Upload a PDF file (multipart/form-data). "
        "Optional `fields` form field: comma-separated names (default: signature, initials)."
    ),
    response_model=DetectionResponseData,
)
async def detect_signatures(
    request: Request,
    file: UploadFile = File(..., description="PDF document to analyze"),
    fields: Optional[str] = Form(None),
) -> DetectionResponseData:
    request_id = getattr(request.state, "request_id", "unknown")

    data = await file.read()
    filename = file.filename or "upload.pdf"

    _pdf_service.validate_bytes(data, file.content_type, filename)

    field_list = _parse_fields_param(fields)
    _validate_field_names(field_list)

    try:
        document = _pdf_service.parse_pdf_bytes(data, filename)
    except PDFParsingError:
        raise

    try:
        results, processing_ms = await _detect_with_timeout(document, field_list)
    except asyncio.TimeoutError:
        logger.warning("Detection timeout for request_id=%s", request_id)
        raise DetectionTimeoutError() from None
    except APIError:
        raise
    except Exception as e:
        logger.exception("Detector failed request_id=%s", request_id)
        raise DetectorRuntimeError(str(e)) from e

    return DetectionResponseData(
        id=f"req-{request_id}",
        timestamp=datetime.now(timezone.utc),
        version="1.0",
        results=results,
        processing_time_ms=processing_ms,
    )
