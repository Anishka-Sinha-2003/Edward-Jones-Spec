---
spec_id: 2603-002
title: REST API Integration
status: defining
phase: design
priority: P0
owner: Team
created: 2026-03-26
updated: 2026-03-26
depends_on: [2603-001]
blocks: []
decisions:
  - framework: FastAPI
  - http-method: POST /detect
  - response-format: JSON with request ID and results array
open_questions:
  - question: Should we support async job callbacks?
    poc: null
  - question: Rate limiting strategy (token bucket, per-IP, per-key)?
    poc: null
---

# Spec 2603-002: REST API Integration

## Overview

REST API endpoint and integration layer that accepts PDF files, invokes the signature detector (2603-001), and returns structured JSON results. This is the user-facing interface to the detection service.

## Problem Statement

Users (Edward Jones applications) need a standardized way to:
- Submit PDF documents for signature detection
- Retrieve detection results in a structured format
- Handle errors gracefully
- Monitor service health

The API must be:
- **Simple**: Easy to call from clients
- **Reliable**: Consistent error handling
- **Observable**: Health checks and metrics
- **Scalable**: Stateless, horizontally scalable

## Solution Approach

Build FastAPI application with:
1. **REST endpoint** for document submission
2. **Request/response contracts** (OpenAPI)
3. **Error handling** with structured responses
4. **Health check** endpoint
5. **Metrics/logging** for monitoring

## Acceptance Criteria

### Functional
- [ ] `POST /detect` endpoint accepts multipart PDF upload
- [ ] Endpoint accepts optional field names parameter
- [ ] Endpoint returns 200 OK with detection results
- [ ] Response includes request ID, timestamp, results
- [ ] Response includes all fields specified
- [ ] Returns 400 Bad Request for invalid PDF
- [ ] Returns 413 Payload Too Large for oversized PDF (>50MB)
- [ ] `GET /health` returns 200 OK when service healthy

### Request/Response Contract
- [ ] OpenAPI schema generated automatically
- [ ] Request examples documented
- [ ] Response examples documented
- [ ] All fields have descriptions and types

### Error Handling
- [ ] Unsupported file format → 400 with error code
- [ ] Missing required fields → 400 with error code
- [ ] PDF parsing error → 500 with error details
- [ ] Timeout → 408 Request Timeout
- [ ] All errors include: code, message, request_id

### Integration
- [ ] API correctly calls detector from 2603-001
- [ ] API propagates detector confidence scores
- [ ] API handles detector exceptions gracefully

### Quality
- [ ] Unit tests for all endpoints
- [ ] Integration tests with mock detector
- [ ] Test coverage >= 80%
- [ ] All endpoints documented
- [ ] Error cases tested

### Performance
- [ ] API responds within 2 seconds (including detection)
- [ ] Concurrent requests processed independently
- [ ] Memory usage tracked per request

## High-Level Design

### API Structure

```
api/
  __init__.py
  main.py                     # FastAPI app initialization
  routes/
    __init__.py
    detection.py              # Detection endpoints
    health.py                 # Health check
    metrics.py                # Prometheus metrics (optional)
  schemas/
    __init__.py
    detection_request.py      # Pydantic models
    detection_response.py
    error_response.py
  middleware/
    __init__.py
    logging.py                # JSON structured logging
    error_handling.py         # Global exception handler
  services/
    __init__.py
    pdf_processing.py         # PDF upload/validation
    detector_service.py       # Integration with 2603-001
tests/
  test_detection_endpoint.py
  test_health_endpoint.py
  test_error_handling.py
  test_schemas.py
```

### Endpoints

#### 1. POST /detect

**Purpose**: Submit PDF for signature/initial detection

**Request**:
```
Content-Type: multipart/form-data

Parameters:
  - file (required): Binary PDF file
  - fields (optional): Comma-separated field names to detect
                       Default: auto-detect from PDF or use defaults
    
Example:
  POST /detect
  file=<binary>
  fields=signature_field_1,initials
```

**Response (200 OK)**:
```json
{
  "id": "req-550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-26T14:30:00.000Z",
  "version": "1.0",
  "results": [
    {
      "field_name": "signature_field_1",
      "status": "present",
      "confidence": 0.95,
      "metadata": {}
    },
    {
      "field_name": "initials",
      "status": "present",
      "confidence": 0.87,
      "metadata": {}
    }
  ],
  "processing_time_ms": 145
}
```

**Error Response (400 Bad Request)**:
```json
{
  "error": {
    "code": "INVALID_PDF_FORMAT",
    "message": "File is not a valid PDF document",
    "request_id": "req-550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Possible Status Codes**:
- 200 OK - Detection succeeded
- 400 Bad Request - Invalid input (malformed PDF, missing file)
- 408 Request Timeout - Detection took too long
- 413 Payload Too Large - PDF exceeds size limit (>50MB)
- 500 Internal Server Error - Unexpected error
- 503 Service Unavailable - Service overloaded

#### 2. GET /health

**Purpose**: Check service health

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-26T14:30:00.000Z",
  "version": "1.0",
  "checks": {
    "detector": "ok",
    "pdf_parser": "ok"
  }
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "timestamp": "2026-03-26T14:30:00.000Z",
  "checks": {
    "detector": "error",
    "reason": "Detector initialization failed"
  }
}
```

### Request/Response Models (Pydantic)

```python
# detection_request.py
class DetectionRequest(BaseModel):
    file: UploadFile  # Binary PDF
    fields: Optional[List[str]] = Field(
        default=["signature", "initials"],
        description="Field names to detect. Defaults to common fields."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "file": "<binary PDF>",
                "fields": ["signature_field_1", "initials"]
            }
        }

# detection_response.py
class FieldDetectionResult(BaseModel):
    field_name: str = Field(..., description="Name of the field detected")
    status: str = Field(
        ..., 
        description="Detection status: present, absent, uncertain"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, le=1.0,
        description="Confidence score (0.0-1.0)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

class DetectionResponseData(BaseModel):
    id: str = Field(..., description="Unique request ID")
    timestamp: datetime = Field(..., description="Server timestamp")
    version: str = Field(default="1.0", description="API version")
    results: List[FieldDetectionResult]
    processing_time_ms: int = Field(..., description="Detection duration in milliseconds")

# error_response.py
class ErrorDetail(BaseModel):
    code: str = Field(..., description="Error code (machine-readable)")
    message: str = Field(..., description="Error message (human-readable)")
    request_id: str = Field(..., description="Request ID for correlation")

class ErrorResponse(BaseModel):
    error: ErrorDetail
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| INVALID_PDF_FORMAT | 400 | File is not a valid PDF |
| INVALID_FILE_TYPE | 400 | File type not supported (must be PDF) |
| FILE_REQUIRED | 400 | No file provided |
| FIELDS_INVALID | 400 | Invalid fields parameter |
| PDF_TOO_LARGE | 413 | PDF exceeds 50MB limit |
| PDF_PARSING_ERROR | 500 | Error parsing PDF content |
| DETECTION_TIMEOUT | 408 | Detection exceeded time limit (5s) |
| DETECTOR_ERROR | 500 | Detector service error |
| INTERNAL_ERROR | 500 | Unexpected server error |

### Implementation Details

#### PDF Processing Service

```python
class PDFProcessingService:
    """Handle PDF upload, validation, and parsing"""
    
    def validate_upload(self, file: UploadFile) -> bool:
        """Validate file is PDF and within size limits"""
        # Check MIME type
        # Check size < 50MB
        # Check magic bytes (PDF header)
        pass
    
    def parse_pdf(self, file: UploadFile) -> PDFDocument:
        """Parse PDF to document object"""
        # Use pdfplumber
        # Extract pages, objects, text
        # Return structured document
        pass
```

#### Detector Service (Integration with 2603-001)

```python
class DetectorService:
    """Integration layer with signature detector"""
    
    def __init__(self, detector: Detector):
        self.detector = detector
    
    def detect_fields(self, 
                      document: PDFDocument, 
                      fields: List[str]
    ) -> List[FieldDetectionResult]:
        """Call detector and format results"""
        # Call detector.detect(document, fields)
        # Convert detector output to API schema
        pass
```

#### Middleware & Logging

```python
# Structured JSON logging for all requests
{
  "timestamp": "2026-03-26T14:30:00.123Z",
  "request_id": "req-uuid",
  "method": "POST",
  "path": "/detect",
  "status": 200,
  "processing_time_ms": 145,
  "file_size_bytes": 2048,
  "fields_requested": ["signature", "initials"],
  "detector_status": "ok",
  "errors": []
}
```

### FastAPI Application Setup

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Signature Detection API",
    description="Detect signatures and initials in PDF documents",
    version="1.0.0"
)

# Add routes
app.include_router(detection.router, prefix="/api/v1")
app.include_router(health.router)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_exception_handler(Exception, global_error_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Integration Points

### With 2603-001 (Detection Core)
- API receives DetectionRequest
- Converts to 2603-001 DetectionRequest format
- Calls detector.detect()
- Maps results back to API response schema
- Gracefully handles detector errors

### Input/Output Flow
```
HTTP Request (multipart)
    ↓
PDFProcessingService.validate_upload()
    ↓
PDFProcessingService.parse_pdf() → PDFDocument
    ↓
DetectorService.detect_fields(document, fields)
    ↓
detector.detect(DetectionRequest) → DetectionResponse [from 2603-001]
    ↓
Format as API response
    ↓
HTTP Response (JSON)
```

## Non-Functional Requirements

- **Performance**: P99 latency < 2 seconds
- **Availability**: 99%+ uptime
- **Throughput**: Support 100+ concurrent requests
- **Rate Limiting**: Plug-in architecture for future rate limiting
- **API Versioning**: URLs use /api/v1 for future compatibility
- **OpenAPI**: Auto-generated documentation at /docs

## Testing Strategy

### Unit Tests
- Request validation (valid/invalid PDF, fields)
- Response formatting
- Error handling
- Schema validation

### Integration Tests
- End-to-end request/response flow
- Mock detector integration
- Error scenarios
- Timeout handling

### Load Tests (Future)
- Concurrent requests
- Large file handling
- Memory/resource usage

## Dependencies

- FastAPI
- uvicorn
- pydantic
- pdfplumber (from 2603-001)
- pytest (testing)
- httpx (testing HTTP)

## Deployment

- Docker image with FastAPI app
- Health check integration with container orchestration
- Environment variables for configuration
- Logging to stdout for container log aggregation

## Future Enhancements

1. **Rate Limiting**: Token bucket, per-IP, API key-based
2. **Authentication**: API key, OAuth2
3. **Async Jobs**: Submit PDF, get job ID, poll for results
4. **Batch Detection**: Multiple PDFs in single request
5. **Webhooks**: Callback URL for async results
6. **Metrics Endpoint**: Prometheus metrics at /metrics
