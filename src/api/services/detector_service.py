"""Bridge HTTP layer to 2603-001 Detector."""

from __future__ import annotations

import logging
import time
from typing import List

from api.schemas.responses import FieldDetectionResult
from signature_detection.detector import Detector
from signature_detection.models import DetectionRequest, PDFDocument

logger = logging.getLogger(__name__)


class DetectorService:
    """Wraps core Detector and maps results to API schema."""

    def __init__(self, detector: Detector) -> None:
        self._detector = detector
        self._logger = logger

    def detect_fields(
        self,
        document: PDFDocument,
        fields: List[str],
    ) -> tuple[list[FieldDetectionResult], int]:
        """Run detection and return API results + processing_time_ms from detector."""
        req = DetectionRequest(document=document, fields=fields)
        start = time.perf_counter()
        resp = self._detector.detect(req)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        # Prefer detector-reported time if set
        proc_ms = resp.processing_time_ms if resp.processing_time_ms else elapsed_ms
        results = [
            FieldDetectionResult(
                field_name=r.field_name,
                status=r.status,
                confidence=r.confidence,
                metadata=dict(r.metadata),
            )
            for r in resp.results
        ]
        return results, proc_ms
