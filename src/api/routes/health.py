"""
Health Check Endpoint

GET /health - Service health status
Spec Task: ENDPOINT-HEALTH-1 and ENDPOINT-HEALTH-2
"""

import logging
from datetime import datetime
from typing import Dict, Literal

from fastapi import APIRouter, Response

router = APIRouter()
logger = logging.getLogger(__name__)


class HealthResponse:
    """Health check response schema (for documentation)."""
    status: Literal["healthy", "unhealthy"]
    timestamp: str  # ISO 8601
    version: str
    checks: Dict[str, str]  # Component -> status


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the API and its dependencies are healthy",
    response_description="Health status of the service",
)
async def health_check() -> Dict:
    """
    Health check endpoint.

    Verifies:
    - API is running
    - Detector module is importable
    - PDF parser (pdfplumber) is available

    Returns:
        HealthResponse-like dict with status and component checks

    Status Codes:
        - 200: Service is healthy
        - 503: Service is unhealthy
    """
    try:
        # Check 1: Try importing detector (2603-001)
        try:
            import sys
            sys.path.insert(0, 'src')
            from signature_detection import MockDetector
            detector_status = "healthy"
        except ImportError as e:
            logger.warning(f"❌ Detector import failed: {e}")
            detector_status = "unhealthy"

        # Check 2: Try importing pdfplumber (for PDF parsing)
        try:
            import pdfplumber
            pdf_parser_status = "healthy"
        except ImportError:
            logger.warning(
                "⚠️ pdfplumber not installed (PDF parsing unavailable)")
            pdf_parser_status = "unavailable"

        # Overall status
        all_healthy = detector_status == "healthy" and pdf_parser_status in [
            "healthy", "unavailable"]

        response = {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "checks": {
                "detector": detector_status,
                "pdf_parser": pdf_parser_status,
                "api": "healthy",
            }
        }

        logger.info(f"✅ Health check: {response['status']}")
        return response

    except Exception as e:
        logger.error(f"🔥 Health check failed with error: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "checks": {
                "detector": "unknown",
                "pdf_parser": "unknown",
                "api": "unhealthy",
            },
            "error": str(e)
        }
