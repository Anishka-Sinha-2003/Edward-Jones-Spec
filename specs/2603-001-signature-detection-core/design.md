---
spec_id: 2603-001
title: Signature Detection Core - Design
phase: planning
updated: 2026-03-26
---

# Design: 2603-001 Signature Detection Core

## Architecture Decisions

### 1. Detector Pattern (Abstract Base + Implementations)

**Decision**: Use abstract base class with concrete implementations to support mocking now and real detectors later.

**Rationale**:
- Decouples detection logic from API layer
- Enables testing without heavy dependencies
- Allows swapping detectors at runtime

**Implementation**:
```python
class Detector(ABC):
    @abstractmethod
    def detect(self, document: PDFDocument, fields: List[str]) -> List[DetectionResult]:
        """Detect signatures in document"""
        pass

class MockDetector(Detector):
    """MVP implementation using heuristics"""
    def detect(self, document, fields):
        # Implementation: see spec.md
        pass

# Future: class MLDetector(Detector): ...
```

### 2. Data Model Design

**Decision**: Use dataclasses for immutable, type-safe result objects.

**Rationale**:
- Clear, explicit types
- Serializable to JSON
- No runtime overhead

**Models**:
```
DetectionResult
  - field_name: str
  - status: str (Literal["present", "absent", "uncertain"])
  - confidence: float
  - metadata: Dict

PDFDocument
  - pages: List[PDFPage]
  - metadata: Dict

PDFPage
  - number: int
  - width: float
  - height: float
  - objects: List[PDFObject]

PDFObject
  - type: str (Literal["text", "image", "shape", "path"])
  - x: float, y: float  # top-left position
  - width: float, height: float
  - content: Any  # text content or image data
```

### 3. Confidence Scoring Strategy

**Decision**: Heuristic-based scoring with rule engine (MVP).

**Rationale**:
- Fast, no ML dependencies
- Deterministic for testing
- Can be replaced with ML model later

**Rules**:
1. Base confidence from detector logic
2. Adjust for field recognition quality
3. Apply realistic noise (±5%)
4. Bound to [0.0, 1.0]

**Example**: Signature field → 95% base, ±5% noise → final 90-100%

### 4. PDF Processing Abstraction

**Decision**: Use pdfplumber for parsing; parse once at API layer, pass structured object to detector.

**Rationale**:
- Detector doesn't depend on PDF library
- API layer handles parsing errors
- Easier to test detector with mock documents

### 5. Error Handling in Detector

**Decision**: Detector returns "uncertain" status for edge cases; API layer converts to HTTP errors.

**Rationale**:
- Detector is composable function
- API layer decides error severity
- Graceful degradation

## Class Diagram

```
┌─────────────────────┐
│   Detector (ABC)    │
├─────────────────────┤
│+ detect()           │
└──────────┬──────────┘
           │
           ├─ MockDetector ✓ (MVP)
           ├─ MLDetector (Future)
           └─ HybridDetector (Future)

┌────────────────────────┐
│  DetectionResult       │
├────────────────────────┤
│+ field_name: str       │
│+ status: str           │
│+ confidence: float     │
│+ metadata: dict        │
└────────────────────────┘

┌────────────────────────┐
│  ConfidenceScorer      │
├────────────────────────┤
│+ score(result): float  │
│+ apply_noise(): float  │
└────────────────────────┘
```

## Mock Detector Algorithm

### Input
- `fields: List[str]` - Field names to detect (e.g., ["signature_field_1", "initials"])

### Algorithm
```
FOR each field IN fields:
  1. Normalize field name to lowercase
  2. Check field type:
     IF contains("signature") AND NOT contains("void"):
       status = "present"
       base_confidence = 0.95
     ELSIF contains("signature") AND contains("void"):
       status = "absent" 
       base_confidence = 0.98
     ELSIF contains("init"):
       status = "present"
       base_confidence = 0.85
     ELSE:
       status = "uncertain"
       base_confidence = 0.50
  3. Apply noise: ±random(0.0, 0.05)
  4. Clamp: confidence = max(0.0, min(1.0, base + noise))
  5. Return DetectionResult(field, status, confidence)
```

### Test Cases
| Input Field | Expected Status | Expected Confidence |
|-------------|-----------------|-------------------|
| signature_field_1 | present | 0.90-1.0 |
| signature_void | absent | 0.93-1.0 |
| initials | present | 0.80-0.90 |
| unknown_field | uncertain | 0.45-0.55 |
| SIGNATURE_TEST (uppercase) | present | 0.90-1.0 |

## Module Organization

### Directory Structure
```
src/
  signature_detection/
    __init__.py                    # Public API exports
    models.py                      # All dataclasses (DetectionResult, etc.)
    detector.py                    # Abstract base class
    scorers.py                     # Confidence scoring logic
    detectors/
      __init__.py
      mock.py                      # MockDetector implementation
    validators.py                  # Input/output validation
    errors.py                      # Custom exceptions

tests/
  test_models.py                   # Test data models
  test_detector_base.py           # Test interface
  test_mock_detector.py           # Test MockDetector logic
  test_scorers.py                 # Test confidence scoring
  test_validators.py              # Test validation
  fixtures/                        # Test data
    sample_documents/
      simple_signature.pdf
      initials_only.pdf
      empty.pdf
```

### Public API (from `__init__.py`)
```python
from .models import DetectionResult, PDFDocument
from .detector import Detector
from .detectors.mock import MockDetector
from .scorers import ConfidenceScorer

__all__ = [
    "DetectionResult",
    "PDFDocument", 
    "Detector",
    "MockDetector",
    "ConfidenceScorer"
]
```

## Implementation Phases

### Phase 1: Data Models & Base Class
1. Define DetectionResult, PDFDocument, PDFPage, PDFObject
2. Define Detector abstract base class
3. Create validation functions

### Phase 2: Mock Detector
1. Implement MockDetector.detect()
2. Implement confidence scoring
3. Add logging

### Phase 3: Testing
1. Unit tests for all models
2. Unit tests for MockDetector
3. Unit tests for confidence scorer
4. Create test fixtures (sample PDFs)
5. Aim for 80%+ coverage

### Phase 4: Documentation
1. Docstrings for all public APIs
2. README with examples
3. Mocking strategy guide for future real detector integration

## Configuration & Constants

```python
# src/signature_detection/config.py
SIGNATURE_FIELD_CONFIDENCE_BASE = 0.95
INITIALS_FIELD_CONFIDENCE_BASE = 0.85
UNCERTAIN_CONFIDENCE_BASE = 0.50
CONFIDENCE_NOISE_RANGE = 0.05  # ±5%
MAX_CONFIDENCE = 1.0
MIN_CONFIDENCE = 0.0
```

## Logging Strategy

**Structured JSON logging for observability**:

```json
{
  "timestamp": "2026-03-26T14:30:00.123Z",
  "level": "INFO",
  "module": "signature_detection.detectors.mock",
  "event": "detection_complete",
  "fields_requested": ["signature_field_1", "initials"],
  "results_count": 2,
  "processing_time_ms": 45,
  "request_id": "req-uuid"
}
```

## Performance Considerations

### Time Complexity
- Mock detector: O(n) where n = number of fields
- Per field: ~1ms string comparison + noise calculation

### Space Complexity
- O(n) output results
- No intermediate data structures

### Benchmarks (Target)
- 10 fields: < 15ms
- 100 fields: < 100ms
- Single typical document: < 100ms

## Testing Strategy

### Unit Test Structure

```python
# tests/test_mock_detector.py
import pytest
from signature_detection.detectors.mock import MockDetector
from signature_detection.models import DetectionResult

class TestMockDetector:
    @pytest.fixture
    def detector(self):
        return MockDetector()
    
    def test_signature_field_detection(self, detector):
        """Signature field should be detected as present"""
        results = detector.detect(["signature_field_1"])
        assert len(results) == 1
        assert results[0].field_name == "signature_field_1"
        assert results[0].status == "present"
        assert 0.90 <= results[0].confidence <= 1.0
    
    def test_void_signature_not_detected(self, detector):
        """Void signature should be detected as absent"""
        results = detector.detect(["signature_void"])
        assert results[0].status == "absent"
        assert 0.93 <= results[0].confidence <= 1.0
    
    def test_initials_detection(self, detector):
        """Initials field should be detected as present"""
        results = detector.detect(["initials"])
        assert results[0].status == "present"
        assert 0.80 <= results[0].confidence <= 0.90
    
    def test_unknown_field(self, detector):
        """Unknown fields should be marked uncertain"""
        results = detector.detect(["unknown_field"])
        assert results[0].status == "uncertain"
        assert 0.45 <= results[0].confidence <= 0.55
    
    def test_multiple_fields(self, detector):
        """Multiple fields should all be processed"""
        fields = ["signature_field_1", "initials", "unknown"]
        results = detector.detect(fields)
        assert len(results) == 3
```

### Coverage Goals
- 80%+ overall coverage
- 100% of MockDetector.detect()
- 95%+ of confidence scoring
- 100% of validation functions

## Dependencies & Version Constraints

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Python | >=3.11 | Language |
| pydantic | >=2.0 | Data validation (for API layer, imported from there) |
| pytest | >=7.0 | Testing |
| pytest-cov | >=4.0 | Coverage reporting |

## Forward Compatibility for Real Detectors

### Extension Point: Custom Detector Implementation

To add a real ML-based detector later:

```python
# src/signature_detection/detectors/ml.py
from signature_detection.detector import Detector

class MLDetector(Detector):
    """Real ML-based signature detection"""
    
    def __init__(self, model_path: str):
        self.model = load_model(model_path)
    
    def detect(self, document: PDFDocument, fields: List[str]) -> List[DetectionResult]:
        """Use ML model for detection"""
        # Extract features from document
        # Call model.predict()
        # Convert predictions to DetectionResult
        pass
```

No changes needed to API or detector interface!

## Security Considerations

- Input fields list: Validated to alphanumeric + underscore
- PDFDocument: Assumed valid from API layer PDF parser
- No external network calls
- No file I/O (parsing done in API layer)

## Summary of Key Decisions

| Decision | Rationale |
|----------|-----------|
| Abstract Detector pattern | Enable swapping implementations |
| Dataclasses for results | Type safety, immutability |
| Heuristic confidence scoring | Simple, testable, replaceable |
| O(n) algorithm | Linear complexity with field count |
| Structured JSON logging | Observability for production |
| Noise injection | Test more realistic scenarios |
| No DB required | Stateless, simpler MVP |
