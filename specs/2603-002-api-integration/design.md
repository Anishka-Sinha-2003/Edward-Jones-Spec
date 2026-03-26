---
spec_id: 2603-002
title: REST API Integration - Design
phase: planning
updated: 2026-03-26
---

# Design: 2603-002 REST API Integration

## Architecture Overview

```
         Client
           ↑↓ HTTP
      ┌─────────────┐
      │  FastAPI    │
      │   App       │
      ├─────────────┤
      │Logging      │
      │Middleware   │
      └──────┬──────┘
             │
      ┌──────┴──────────────┐
      ↓                     ↓
 [Detection Route]    [Health Route]
      ↑                     ↓
      │              Status Check
      │
 [PDFProcessing]
      ↑
      │
 [DetectorService] → [2603-001 Detector]
```

## Design Decisions

### 1. Framework Selection: FastAPI

**Decision**: Use FastAPI for REST API.

**Rationale**:
- Native async/await support for concurrent requests
- Automatic OpenAPI/Swagger documentation
- Built-in validation via Pydantic
- High performance (ASGI)
- Excellent error handling
- Great for Python ecosystem

**Alternative Rejected**: Flask (less async, more boilerplate)

### 2. Request Handling: Multipart File Upload

**Decision**: Accept PDF as multipart form data with optional fields parameter.

**Rationale**:
- Standard for file uploads
- Supported by all HTTP clients
- Easy to test with curl/Postman
- Optional fields parameter for flexibility

**Example**:
```
POST /api/v1/detect
Content-Type: multipart/form-data

file: <PDF binary>
fields: signature_field_1,initials
```

### 3. Response Format: Versioned JSON

**Decision**: Return structured JSON with request ID, timestamp, results array.

**Rationale**:
- Machine-readable and processable
- Request ID enables tracing
- Timestamp for auditing
- Extensible for future fields
- Version field supports backward compatibility

### 4. Error Handling: Structured JSON Errors

**Decision**: All errors return structured JSON with code, message, request_id.

**Rationale**:
- Consistent error experience
- Machine-readable error codes
- Request ID for correlation/debugging
- HTTP status codes + detailed codes

### 5. Validation: Pydantic Models

**Decision**: Use Pydantic for request/response validation.

**Rationale**:
- Automatic validation
- Clear error messages
- Type hints
- JSON Schema generation
- Coercion (e.g., string to list)

### 6. PDF Processing: Library Abstraction

**Decision**: Use pdfplumber for parsing; abstract in service layer.

**Rationale**:
- Reliable PDF handling
- Structured object extraction
- Good performance
- Replaceable for future improvements

### 7. Dependency Injection: Constructor Injection

**Decision**: Inject detector and services into routes.

**Rationale**:
- Easy to test (mock dependencies)
- Testable without HTTP calls
- Clear dependencies
- Follows SOLID principles

## Class Diagram

```
┌─────────────────────────────────┐
│   FastAPI Application           │
├─────────────────────────────────┤
│+ detection_router()             │
│+ health_router()                │
└────────────┬────────────────────┘
             │
     ┌───────┴────────┐
     ↓                ↓
┌───────────────┐  ┌──────────┐
│DetectionRoute │  │HealthRoute
├───────────────┤  ├──────────┤
│+ POST /detect │  │+ GET     │
└───────┬───────┘  │ /health  │
        ↑          └──────────┘
        │
  ┌─────┴────────────────┐
  ↓                      ↓
┌──────────────┐    ┌──────────────┐
│PDFProcessing │    │DetectorService
│Service       │    ├──────────────┤
├──────────────┤    │+ detect_fields()
│+ validate()  │    └──────┬───────┘
│+ parse()     │           │
└──────────────┘           ↓
                    ┌──────────────┐
                    │2603-001      │
                    │Detector      │
                    └──────────────┘

┌─────────────────────┐
│Pydantic Models      │
├─────────────────────┤
│DetectionRequest     │
│FieldDetectionResult │
│DetectionResponse    │
│ErrorResponse        │
└─────────────────────┘
```

## Request/Response Flow

### Successful Request

```
1. HTTP POST /api/v1/detect
   ↓
2. FastAPI validates multipart form data
   ✓ file: PDF uploaded
   ✓ fields: Optional list (defaults to ["signature", "initials"])
   ↓
3. PDFProcessingService.validate_upload()
   - Check MIME type: application/pdf
   - Check size: < 50MB
   - Check magic bytes: %PDF
   ✓ Valid → continue
   ✗ Invalid → 400 Bad Request
   ↓
4. PDFProcessingService.parse_pdf()
   - Use pdfplumber
   - Extract pages, objects, text
   - Build PDFDocument structure
   ↓
5. DetectorService.detect_fields()
   - Create DetectionRequest for 2603-001
   - Call detector.detect()
   - Get DetectionResponse
   ↓
6. Format API response
   - Add request ID (UUID)
   - Add timestamp (ISO 8601)
   - Add API version
   - Include results
   - Add processing time
   ↓
7. HTTP 200 OK + JSON body
```

### Error Handling

```
Error Scenario → Status Code → Error Code → Message

File not PDF → 400 → INVALID_PDF_FORMAT → Not a valid PDF
File > 50MB → 413 → PDF_TOO_LARGE → Exceeds size limit
No file → 400 → FILE_REQUIRED → Please upload a PDF
Fields invalid → 400 → FIELDS_INVALID → Fields must be alphanumeric
PDF parsing error → 500 → PDF_PARSING_ERROR → Failed to parse PDF
Detector error → 500 → DETECTOR_ERROR → Detection failed
Timeout (>5s) → 408 → DETECTION_TIMEOUT → Processing took too long
```

## Service Layer Design

### PDFProcessingService

```python
class PDFProcessingService:
    """Handle PDF upload validation and parsing"""
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_MIME_TYPES = ["application/pdf"]
    PDF_MAGIC_BYTES = b"%PDF"
    
    async def validate_upload(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate uploaded file is a PDF
        
        Returns:
            (is_valid, error_message)
        """
        # 1. Check file size
        # 2. Check MIME type
        # 3. Check magic bytes
        # 4. Return validation result
        pass
    
    async def parse_pdf(self, file: UploadFile) -> PDFDocument:
        """Parse PDF to structured document
        
        Returns:
            PDFDocument with pages and objects
            
        Raises:
            PDFParsingError: If parsing fails
        """
        # 1. Read file content
        # 2. Use pdfplumber to parse
        # 3. Extract pages, objects, text
        # 4. Build PDFDocument
        pass
```

### DetectorService

```python
class DetectorService:
    """Integration with 2603-001 detector"""
    
    def __init__(self, detector: Detector):
        self.detector = detector
    
    async def detect_fields(self,
                            document: PDFDocument,
                            fields: List[str],
                            request_id: str
    ) -> DetectionResponse:
        """Call detector and format results
        
        Args:
            document: Parsed PDF document
            fields: Field names to detect
            request_id: For logging/tracing
            
        Returns:
            DetectionResponse with results
            
        Raises:
            DetectorError: If detection fails
        """
        # 1. Validate fields input
        # 2. Create DetectionRequest (2603-001 format)
        # 3. Call detector.detect()
        # 4. Convert results to API schema
        # 5. Return formatted response
        pass
```

## FastAPI Application Structure

```python
# api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json

# Initialize
app = FastAPI(
    title="Signature Detection API",
    description="Detect signatures and initials in PDF documents",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Middleware for structured logging
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    import time
    import uuid
    
    request_id = str(uuid.uuid4())
    start = time.time()
    
    response = await call_next(request)
    
    duration = (time.time() - start) * 1000
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": duration
    }
    
    logger.info(json.dumps(log_entry))
    response.headers["X-Request-ID"] = request_id
    
    return response

# Routes
@app.post("/api/v1/detect")
async def detect_signatures(
    file: UploadFile = File(...),
    fields: Optional[str] = Query(None)
) -> DetectionResponseData:
    """Detect signatures and initials in PDF"""
    # Implementation (see below)
    pass

@app.get("/health")
async def health_check() -> HealthResponse:
    """Service health check"""
    # Implementation
    pass

# Exception handlers
@app.exception_handler(PDFValidationError)
async def pdf_validation_handler(request: Request, exc: PDFValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "INVALID_PDF_FORMAT",
                "message": str(exc),
                "request_id": request.headers.get("X-Request-ID")
            }
        }
    )

# Startup/shutdown
@app.on_event("startup")
async def startup():
    # Initialize detector, services
    pass

@app.on_event("shutdown")
async def shutdown():
    # Cleanup
    pass
```

## Endpoint Implementation Details

### POST /api/v1/detect

```python
@app.post("/api/v1/detect", response_model=DetectionResponseData)
async def detect_signatures(
    file: UploadFile = File(...),
    fields: Optional[str] = Query(None)
) -> DetectionResponseData:
    """
    Detect signatures and initials in a PDF document.
    
    Args:
        file: PDF file to analyze
        fields: Comma-separated field names (optional)
                Default: signature,initials
    
    Returns:
        Detection results with confidence scores
        
    Raises:
        400: Invalid PDF or parameters
        408: Processing timeout
        413: File too large
        500: Server error
    """
    import time
    import uuid
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # 1. Parse fields parameter
        if fields:
            field_list = [f.strip() for f in fields.split(",")]
        else:
            field_list = ["signature", "initials"]
        
        # 2. Validate file
        is_valid, error_msg = await pdf_service.validate_upload(file)
        if not is_valid:
            raise PDFValidationError(error_msg)
        
        # 3. Parse PDF
        document = await pdf_service.parse_pdf(file)
        
        # 4. Detect signatures
        response = await detector_service.detect_fields(
            document,
            field_list,
            request_id
        )
        
        # 5. Calculate processing time
        processing_ms = int((time.time() - start_time) * 1000)
        
        # 6. Return response
        return DetectionResponseData(
            id=request_id,
            timestamp=datetime.utcnow(),
            version="1.0",
            results=response.results,
            processing_time_ms=processing_ms
        )
        
    except PDFValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileTooLargeError:
        raise HTTPException(status_code=413, detail="File too large")
    except TimeoutError:
        raise HTTPException(status_code=408, detail="Processing timeout")
    except Exception as e:
        logger.error(f"Detection error: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Internal server error")
```

### GET /health

```python
@app.get("/health")
async def health_check() -> HealthResponse:
    """Check service health and dependencies"""
    
    checks = {
        "detector": "ok",
        "pdf_parser": "ok"
    }
    
    try:
        # Test detector initialization
        _ = detector  # Verify accessible
    except Exception as e:
        checks["detector"] = f"error: {str(e)}"
    
    status = "healthy" if all(v == "ok" for v in checks.values()) else "unhealthy"
    
    return HealthResponse(
        status=status,
        timestamp=datetime.utcnow(),
        version="1.0",
        checks=checks
    )
```

## Data Model Validation

### DetectionRequest (Pydantic)

```python
class DetectionRequest(BaseModel):
    """Request for signature detection"""
    
    file: UploadFile
    fields: Optional[List[str]] = Field(
        default=["signature", "initials"],
        min_items=1,
        max_items=100,
        description="Field names to detect"
    )
    
    @field_validator("fields")
    def validate_fields(cls, v):
        """Ensure fields are alphanumeric and underscore only"""
        if v:
            for field in v:
                if not re.match(r"^[a-zA-Z0-9_]+$", field):
                    raise ValueError(f"Invalid field name: {field}")
        return v
```

### FieldDetectionResult (Pydantic)

```python
class FieldDetectionResult(BaseModel):
    """Result for single field detection"""
    
    field_name: str = Field(..., description="Field name")
    status: Literal["present", "absent", "uncertain"] = Field(
        ...,
        description="Detection status"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field_name": "signature_field_1",
                "status": "present",
                "confidence": 0.95,
                "metadata": {}
            }
        }
    )
```

### DetectionResponseData (Pydantic)

```python
class DetectionResponseData(BaseModel):
    """Complete detection response"""
    
    id: str = Field(..., description="Request UUID")
    timestamp: datetime = Field(..., description="Server timestamp")
    version: str = Field(default="1.0", description="API version")
    results: List[FieldDetectionResult]
    processing_time_ms: int = Field(..., ge=0)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() + "Z"
        }
    )
```

## Testing Strategy

### Unit Tests

```python
# tests/test_detection_endpoint.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from api.main import app
    return TestClient(app)

class TestDetectionEndpoint:
    def test_detect_valid_pdf(self, client):
        """Valid PDF returns 200 with results"""
        with open("tests/fixtures/simple.pdf", "rb") as f:
            response = client.post(
                "/api/v1/detect",
                files={"file": f},
                params={"fields": "signature_field_1,initials"}
            )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "results" in data
        assert len(data["results"]) == 2
    
    def test_detect_invalid_pdf(self, client):
        """Invalid file returns 400"""
        response = client.post(
            "/api/v1/detect",
            files={"file": ("test.txt", b"not a pdf", "text/plain")}
        )
        assert response.status_code == 400
    
    def test_detect_no_file(self, client):
        """Missing file returns 400"""
        response = client.post("/api/v1/detect")
        assert response.status_code == 400
    
    def test_detect_default_fields(self, client):
        """Default fields used if not specified"""
        with open("tests/fixtures/simple.pdf", "rb") as f:
            response = client.post("/api/v1/detect", files={"file": f})
        assert response.status_code == 200

class TestHealthEndpoint:
    def test_health_check(self, client):
        """Health endpoint returns 200 when healthy"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
```

### Integration Tests

- End-to-end with mock detector
- Error scenarios
- Concurrent requests
- Large PDF handling

## Performance & Scaling

### Concurrency Strategy
- FastAPI handles concurrent requests natively
- Each request gets separate thread/coroutine
- No shared mutable state
- Detector can be safely called concurrently

### Resource Limits
- Max file size: 50MB
- Max concurrent requests: Limited by OS file descriptors
- Max memory per request: ~500MB (PDF + processing)

### Monitoring
- Log all requests with duration
- Track error rates
- Measure detector latency
- Export metrics for dashboard

## Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## CI/CD Integration

### Pre-deploy Checks
- Lint (pylint, flake8)
- Type check (mypy)
- Test (pytest)
- Coverage (>80%)
- Build Docker image

### Deployment
- Tag image
- Push to registry
- Deploy to staging
- Health check
- Deploy to production

## Security

### Input Validation
- File MIME type check
- Magic bytes verification  
- Size limits enforced
- Field names alphanumeric only

### Error Messages
- Generic messages in HTTP response
- Detailed logs server-side only

### Rate Limiting (Future)
- Per-IP limits
- Per-API-key limits
- Token bucket algorithm
