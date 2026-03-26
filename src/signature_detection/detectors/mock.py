"""Mock Detector Implementation - MVP signature detection using heuristic rules.

This module provides MockDetector, a simple rule-based implementation of the Detector
interface for MVP testing. It simulates signature and initial detection using field
name patterns and confidence scoring.

Algorithm:
    For each field in the request:
    1. Normalize field name to lowercase
    2. Identify field type (signature, void, initials, or unknown)
    3. Get base confidence from ConfidenceScorer
    4. Apply randomness (±5%) for realism
    5. Return DetectionResult with status and confidence

Example:
    >>> from signature_detection.detectors.mock import MockDetector
    >>> from signature_detection.models import PDFDocument, PDFPage, DetectionRequest
    >>> detector = MockDetector()
    >>> doc = PDFDocument(pages=[PDFPage(1, 800, 600, [])])
    >>> request = DetectionRequest(doc, ["signature_1", "initials"])
    >>> response = detector.detect(request)
    >>> print(response.results[0])
    DetectionResult(field_name='signature_1', status='present', confidence=0.95, metadata={})
"""

import time
import logging
from typing import List

from signature_detection.detector import Detector
from signature_detection.models import DetectionRequest, DetectionResponse, DetectionResult
from signature_detection.scorers import ConfidenceScorer


logger = logging.getLogger(__name__)


class MockDetector(Detector):
    """Mock detector for MVP - uses heuristic rules to simulate signature detection.

    Supports detection patterns for:
    - Signatures: fields containing "signature" (not "void")
    - Void signatures: fields containing both "signature" and "void"
    - Initials: fields containing "init"
    - Unknown: any other field

    Attributes:
        SUPPORTED_PATTERNS (list): Field name patterns this detector recognizes
    """

    SUPPORTED_PATTERNS = ["signature", "initials", "init", "void"]

    def detect(self, request: DetectionRequest) -> DetectionResponse:
        """Detect signatures in document using heuristic rules.

        For each field in request.fields:
        1. Normalize to lowercase
        2. Determine field type from patterns
        3. Assign status (present/absent/uncertain)
        4. Calculate confidence score with noise
        5. Build DetectionResult

        Args:
            request: DetectionRequest containing document and fields to detect

        Returns:
            DetectionResponse with list of DetectionResults and processing time

        Raises:
            None - returns "uncertain" for unrecognized patterns
        """
        start_time = time.time()
        results = []

        # Process each field in the request
        for field_name in request.fields:
            # Step 1: Normalize field name to lowercase for pattern matching
            field_lower = field_name.lower()

            # Step 2: Determine field type and assign initial status
            status, base_confidence = self._classify_field(field_lower)

            # Step 3: Apply confidence scoring with noise
            final_confidence = ConfidenceScorer.score(
                field_name, apply_random_noise=True)

            # Step 4: Create DetectionResult
            result = DetectionResult(
                field_name=field_name,
                status=status,
                confidence=final_confidence,
                metadata={
                    "detector": "MockDetector",
                    "pattern": self._get_pattern(field_lower),
                    "base_confidence": base_confidence
                }
            )

            results.append(result)

            # Log detection
            logger.debug(
                f"Detected field '{field_name}': status={status}, confidence={final_confidence:.2f}"
            )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Return structured response
        response = DetectionResponse(
            results=results,
            processing_time_ms=processing_time_ms
        )

        logger.info(
            f"Detection complete: {len(results)} fields processed in {processing_time_ms}ms"
        )

        return response

    def supports_field(self, field_name: str) -> bool:
        """Check if this detector supports a specific field.

        Supports any field that contains recognizable patterns:
        - Contains "signature" (with or without "void")
        - Contains "initial" or "init"
        - Unknown fields return False (uncertain status instead)

        Args:
            field_name: Name of field to check

        Returns:
            True if field matches supported patterns, False otherwise

        Example:
            >>> detector = MockDetector()
            >>> detector.supports_field("signature_1")
            True
            >>> detector.supports_field("initials")
            True
            >>> detector.supports_field("unknown_field")
            False
        """
        field_lower = field_name.lower()

        # Check for recognized patterns
        # Exclude "void" from direct check
        for pattern in self.SUPPORTED_PATTERNS[:-1]:
            if pattern in field_lower:
                return True

        return False

    def _classify_field(self, field_lower: str) -> tuple:
        """Classify field type and assign initial status and base confidence.

        Implements the field classification algorithm:
        1. If contains "signature" AND "void" → status="absent", confidence=0.98
        2. Else if contains "signature" → status="present", confidence=0.95
        3. Else if contains "init" → status="present", confidence=0.85
        4. Else → status="uncertain", confidence=0.50

        Args:
            field_lower: Field name in lowercase

        Returns:
            Tuple of (status, base_confidence)
            status: Literal["present", "absent", "uncertain"]
            base_confidence: float between 0.0 and 1.0
        """
        # Rule 1: Void signatures (signature + void)
        if "signature" in field_lower and "void" in field_lower:
            return ("absent", 0.98)

        # Rule 2: Regular signatures (signature but not void)
        elif "signature" in field_lower:
            return ("present", 0.95)

        # Rule 3: Initials
        elif "init" in field_lower:
            return ("present", 0.85)

        # Rule 4: Unknown fields
        else:
            return ("uncertain", 0.50)

    def _get_pattern(self, field_lower: str) -> str:
        """Get the matching pattern for a field.

        Helper method to identify which pattern matched during classification.

        Args:
            field_lower: Field name in lowercase

        Returns:
            String name of the matched pattern or "unknown"
        """
        if "signature" in field_lower and "void" in field_lower:
            return "signature_void"
        elif "signature" in field_lower:
            return "signature"
        elif "init" in field_lower:
            return "initials"
        else:
            return "unknown"


__all__ = ["MockDetector"]
