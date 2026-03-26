---
spec_id: 2603-001
title: Signature Detection Core
status: defining
phase: design
priority: P0
owner: Team
created: 2026-03-26
updated: 2026-03-26
depends_on: []
blocks: [2603-002]
decisions:
  - mocking-strategy: Position-based rule heuristic
  - confidence-model: Heuristic (0.0-1.0)
open_questions:
  - question: Should we support custom field coordinates?
    poc: null
  - question: What PDF variations should mock handle?
    poc: null
---

# Spec 2603-001: Signature Detection Core

## Overview

Core detection module that identifies signatures and initials in PDF documents. MVP uses mocking; abstracts detection logic for future real model integration.

## Problem Statement

Edward Jones needs to automatically detect where signatures and initials appear in PDF documents to enable document processing workflows. The detection must be:
- **Reliable**: Correctly identify presence/absence
- **Scorable**: Provide confidence measure
- **Testable**: Work with test PDFs
- **Extensible**: Ready for real ML models

## Solution Approach

Build a detection module with:
1. **Mocked detector**: Position-based heuristics for MVP testing
2. **Detector interface**: Allows swapping implementations
3. **Confidence scoring**: Rule-based confidence calculation
4. **Test coverage**: Unit tests with mock PDFs

## Acceptance Criteria

### Functional
- [ ] Detector accepts parsed PDF document object
- [ ] Detector identifies signature field in document
- [ ] Detector identifies initials field in document
- [ ] Detector returns status (present/absent/uncertain)
- [ ] Detector provides confidence score (0-1)
- [ ] Detector handles missing fields gracefully

### Quality
- [ ] Unit tests cover all detector code paths
- [ ] Test coverage >= 80%
- [ ] Mocking implementation documented
- [ ] Detection rules documented and justifiable
- [ ] All edge cases (empty PDF, single field, multiple fields) tested

### Performance
- [ ] Detection completes within 100ms for typical document
- [ ] Memory usage < 50MB for single document

### Integration Points
- [ ] Detector is callable from API layer
- [ ] Detector returns structured output
- [ ] Detector supports field list as input
- [ ] Detector can be mocked in API tests

## High-Level Design

### Module Structure

```
signature_detection/
  __init__.py
  models/
    __init__.py
    detection_result.py       # DataClass: field_name, status, confidence
    detector_base.py          # Abstract base for detectors
  detectors/
    __init__.py
    mock_detector.py          # MVP mocked implementation
    # future: ml_detector.py
  scoring/
    __init__.py
    confidence_scorer.py      # Confidence calculation rules
  utils/
    __init__.py
    validation.py             # PDF/field validation
tests/
  test_detection_result.py
  test_mock_detector.py
  test_confidence_scorer.py
  test_validation.py
  fixtures/
    test_document_1.pdf       # Simple signature
    test_document_2.pdf       # Initials only
    test_document_3.pdf       # Empty
```

### Model Definitions

#### DetectionResult
```python
@dataclass
class DetectionResult:
    """Single field detection result"""
    field_name: str              # e.g. "signature_field_1"
    status: str                  # "present" | "absent" | "uncertain"
    confidence: float            # 0.0 - 1.0
    metadata: Dict[str, Any]     # Additional context (position, size, etc.)
```

#### DetectionRequest
```python
@dataclass
class DetectionRequest:
    """Request for detection"""
    document: PDFDocument        # Parsed PDF object
    fields: List[str]            # Field names to detect
```

#### DetectionResponse
```python
@dataclass
class DetectionResponse:
    """Success response from detector"""
    results: List[DetectionResult]
    processing_time_ms: int
```

### Detector Interface

```python
class Detector(ABC):
    """Abstract base for signature/initial detectors"""
    
    def detect(self, request: DetectionRequest) -> DetectionResponse:
        """Detect signatures/initials in document"""
        pass
    
    def supports_field(self, field_name: str) -> bool:
        """Check if detector recognizes field"""
        pass
```

### Mock Detector Behavior

The MVP mock detector uses simple heuristics:

**Rules**:
1. **Signature detection**: Check if field name contains "signature" or "sig"
   - If yes: 95% confidence "present"
   - Exception: If field name contains "void": 98% confidence "absent"

2. **Initials detection**: Check if field name contains "init" or "initials"
   - If yes: 85% confidence "present"

3. **Confidence adjustment**: Add ±5% randomness for realistic variation

**Example Logic**:
```python
def detect_in_mock(fields: List[str]) -> List[DetectionResult]:
    results = []
    for field in fields:
        if "signature" in field.lower():
            status = "absent" if "void" in field.lower() else "present"
            confidence = 0.98 if "void" in field.lower() else 0.95
        elif "init" in field.lower():
            status = "present"
            confidence = 0.85
        else:
            status = "uncertain"
            confidence = 0.50
        
        results.append(DetectionResult(
            field_name=field,
            status=status,
            confidence=add_randomness(confidence, ±0.05)
        ))
    return results
```

### Confidence Scoring

**Scorer Rules**:
- **Perfect confidence**: 0.95-1.0 (high certainty)
- **High confidence**: 0.80-0.94 (good certainty)
- **Medium confidence**: 0.50-0.79 (uncertain)
- **Low confidence**: 0.0-0.49 (very uncertain)

**Heuristics**:
1. Base confidence from detector rules
2. Adjust for field clarity (text vs image - mock assumes clear)
3. Add noise for realism (±5%)
4. Clamp to [0.0, 1.0]

## Data Models

### PDF Document Input
```
Assumed: PDF parsed by API layer into structured format:
{
  "pages": [
    {
      "width": 612,
      "height": 792,
      "objects":  [
        {"type": "text", "value": "Signature:", "x": 50, "y": 700},
        {"type": "image", "x": 150, "y": 680, "width": 100, "height": 40}
      ]
    }
  ]
}
```

### Output Format
```json
{
  "signature_field_1": {
    "field_name": "signature_field_1",
    "status": "present",
    "confidence": 0.95,
    "metadata": {}
  },
  "initials": {
    "field_name": "initials",
    "status": "present",
    "confidence": 0.87,
    "metadata": {}
  }
}
```

## Implementation Tasks

(Detailed in 2603-001-tasks.md after design approval)

Key work streams:
1. Define data models and base classes
2. Implement mock detector
3. Implement confidence scorer
4. Write comprehensive unit tests
5. Document mocking strategy for future real implementation

## Testing Strategy

### Unit Tests
- Mock detector logic correctness
- Edge cases (empty fields list, unknown field names)
- Confidence scoring boundaries
- PDF parsing error handling

### Test Fixtures
- Simple PDF with signature placeholder
- PDF with initials only
- Empty PDF
- PDF with mixed fields

### Coverage Target
- 80%+ overall
- 100% of detector code paths
- 95%+ of confidence scoring

## Non-Functional Requirements

- **Performance**: Detection < 100ms per document
- **Memory**: < 50MB per request
- **Compatibility**: Python 3.11+
- **Logging**: Structured JSON logs with request ID, duration
- **Error Handling**: Fail gracefully with clear error messages

## Dependencies & Assumptions

### Dependencies
- Python 3.11+
- pdfplumber (for PDF parsing, added by 2603-002)
- pytest (testing)

### Assumptions
- PDF is well-formed and parseable
- Field names are lowercase alphanumeric
- Confidence scoring is heuristic for MVP
- Mocking is acceptable for MVP phase

## Open Questions

1. **Custom field coordinates**: Should users specify exact page/coordinates for field detection?
   - Decision: No for MVP. Use field name inference only.
   
2. **PDF variations**: What PDF structures should the mock handle?
   - Decision: Standard form PDFs with text labels + placeholder areas.
   
3. **Batch detection**: Should detector handle multiple documents in one call?
   - Decision: No for MVP. Single document per request.

## Rollout & Future

**MVP (2603-001)**:
- Mocked detector
- Confidence scoring
- Test coverage

**Phase 2 (Future - not in MVP)**:
- Real ML-based detector
- Improved confidence model
- Additional signature types (digital, handwritten)
- Batch processing
