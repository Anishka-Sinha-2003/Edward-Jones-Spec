"""Confidence scoring logic for detection results."""

import random

__all__ = ["ConfidenceScorer"]


class ConfidenceScorer:
    """Heuristic-based confidence scoring for detection results.

    MVP implementation that uses rule-based scoring with noise for realism.
    Can be replaced with ML-based scoring in future versions.
    """

    # Base confidence values by field type
    SIGNATURE_CONFIDENCE = 0.95
    INITIALS_CONFIDENCE = 0.85
    VOID_CONFIDENCE = 0.98
    UNCERTAIN_CONFIDENCE = 0.50

    # Noise for realistic variability
    NOISE_RANGE = 0.05  # ±5%

    @staticmethod
    def apply_base_confidence(field_type: str) -> float:
        """Get base confidence for field type.

        Args:
            field_type: Type of field ("signature", "initials", "void", or other)

        Returns:
            Base confidence score (before noise)
        """
        field_lower = field_type.lower()

        if "void" in field_lower:
            return ConfidenceScorer.VOID_CONFIDENCE
        elif "signature" in field_lower:
            return ConfidenceScorer.SIGNATURE_CONFIDENCE
        elif "init" in field_lower:
            return ConfidenceScorer.INITIALS_CONFIDENCE
        else:
            return ConfidenceScorer.UNCERTAIN_CONFIDENCE

    @staticmethod
    def apply_noise(base_confidence: float) -> float:
        """Add random noise to confidence for realism.

        Args:
            base_confidence: Base confidence before noise

        Returns:
            Confidence with ±5% noise applied
        """
        noise = random.uniform(-ConfidenceScorer.NOISE_RANGE,
                               ConfidenceScorer.NOISE_RANGE)
        confidence = base_confidence + noise
        return ConfidenceScorer.validate_confidence(confidence)

    @staticmethod
    def validate_confidence(score: float) -> float:
        """Clamp confidence to valid range [0.0, 1.0].

        Args:
            score: Confidence score to validate

        Returns:
            Confidence clamped to [0.0, 1.0]
        """
        return max(0.0, min(1.0, score))

    @staticmethod
    def score(field_name: str, apply_random_noise: bool = True) -> float:
        """Calculate confidence score for a field.

        Args:
            field_name: Name of the field being detected
            apply_random_noise: Whether to apply realistic noise (default: True)

        Returns:
            Final confidence score (0.0-1.0)
        """
        base = ConfidenceScorer.apply_base_confidence(field_name)

        if apply_random_noise:
            return ConfidenceScorer.apply_noise(base)
        else:
            return base
