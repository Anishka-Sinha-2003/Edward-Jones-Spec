"""
Detection Endpoint

POST /api/v1/detect - Detect signatures in a document
Spec Task: ENDPOINT-DETECT-1 through ENDPOINT-DETECT-4 (minimal implementation)
"""

from signature_detection.models import (
    DetectionRequest,
    DetectionResponse,
    PDFDocument,
    PDFPage,
    PDFObject,
)
from signature_detection import MockDetector
import logging
import sys
import time
from typing import Optional, List

from fastapi import APIRouter, HTTPException

# Import detection models from 2603-001
sys.path.insert(0, 'src')

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize detector once (singleton)
detector = MockDetector()


class SimpleDetectRequest:
    """
    Minimal request schema for JSON input.
    This is simpler than full PDF upload - just specify fields to detect.
    """
    fields: Optional[List[str]] = None  # Defaults to ["signature", "initials"]


@router.post(
    "/api/v1/detect",
    summary="Detect Signatures",
    description="Detect signature fields in a document",
)
async def detect_signatures(request: dict) -> dict:
    """
    Minimal POST /detect endpoint.

    Request body (JSON):
        {
            "fields": ["signature_field_1", "signature_void", "initials"]
        }

    Response (200 OK):
        {
            "results": [
                {
                    "field_name": "signature_field_1",
                    "status": "present",
                    "confidence": 0.92,
                    "metadata": {}
                },
                ...
            ],
            "processing_time_ms": 5
        }

    How it works:
        1. Accept JSON request with list of field names
        2. Create mock PDFDocument (2-page document)
        3. Call MockDetector.detect() with DetectionRequest
        4. Return structured DetectionResponse

    Raises:
        HTTPException 400: Invalid field names
        HTTPException 500: Detector error
    """
    try:
        # Extract fields from request
        fields = request.get("fields", ["signature_field_1", "initials"])

        if not fields:
            raise HTTPException(
                status_code=400,
                detail="fields list cannot be empty"
            )

        logger.info(f"📝 Detect request: {len(fields)} fields")

        # Start timer
        start_time = time.time()

        # Create a mock PDFDocument (2-page document with test content)
        # This is a simplified approach - in real API, would parse uploaded PDF
        pages = [
            PDFPage(
                number=1,
                width=612,  # Standard letter width in points
                height=792,  # Standard letter height in points
                objects=[
                    PDFObject(
                        obj_type="text",
                        x=100, y=100, width=200, height=50,
                        content="Page 1 - Signature Section"
                    )
                ]
            ),
            PDFPage(
                number=2,
                width=612,
                height=792,
                objects=[
                    PDFObject(
                        obj_type="text",
                        x=100, y=100, width=200, height=50,
                        content="Page 2 - Initials Section"
                    )
                ]
            ),
        ]

        document = PDFDocument(
            pages=pages,
            metadata={"name": "test_document.pdf", "pages": 2}
        )

        logger.debug(f"📄 Created mock document: {len(pages)} pages")

        # Create detection request for 2603-001 detector
        detection_request = DetectionRequest(
            document=document,
            fields=fields
        )

        logger.debug(f"🔍 Calling MockDetector.detect()...")

        # Call detector
        detection_response = detector.detect(detection_request)

        # Calculate processing time
        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"✅ Detection complete: {len(detection_response.results)} results, "
            f"{elapsed_ms}ms"
        )

        # Return response as dict (FastAPI auto-serializes)
        return {
            "results": [
                {
                    "field_name": result.field_name,
                    "status": result.status,
                    "confidence": result.confidence,
                    "metadata": result.metadata,
                }
                for result in detection_response.results
            ],
            "processing_time_ms": elapsed_ms,
        }

    except ValueError as e:
        logger.warning(f"⚠️ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"🔥 Detection error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Detection failed - see logs for details"
        )
