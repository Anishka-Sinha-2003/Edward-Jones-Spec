---
spec_id: 2603-002
title: REST API Integration - Tasks
phase: ready
updated: 2026-03-26
total_tasks: 28
depends_on: [2603-001]
---

# Tasks: 2603-002 REST API Integration

## Overview

Implementation tasks for REST API layer. Depends on 2603-001 completion. Estimated effort: 4-5 days for 1-2 developers.

## Prerequisites

- [ ] **PREREQ-1** [P0] Verify 2603-001 completion
  - Core detection module implemented
  - Tests passing, coverage >= 80%
  - Detector interface available for import
  - **Acceptance**: Can import `from signature_detection import Detector, MockDetector`

## Project Structure Setup

- [ ] **SETUP-1** [P0] Create API project directory structure
  - `api/` directory with: main.py, routes/, schemas/, middleware/, services/
  - `tests/` directory with test files
  - `infra/` directory for Docker and deployment
  - **Acceptance**: All directories verified

- [ ] **SETUP-2** [P0] Initialize FastAPI application
  - Create `api/main.py` with FastAPI app
  - Configure CORS middleware (optional for MVP)
  - Setup logging infrastructure
  - **Acceptance**: App instantiates without errors

## Pydantic Models & Schemas

- [ ] **SCHEMA-1** [P0] Create DetectionRequest model
  - file: UploadFile (required)
  - fields: Optional[List[str]] (defaults to ["signature", "initials"])
  - Add field validators for alphanumeric field names
  - **Acceptance**: Model validates correct/incorrect inputs

- [ ] **SCHEMA-2** [P0] Create FieldDetectionResult model
  - field_name: str
  - status: Literal["present", "absent", "uncertain"]
  - confidence: float (0.0-1.0 with bounds check)
  - metadata: Dict[str, Any]
  - **Acceptance**: Model instantiates and serializes

- [ ] **SCHEMA-3** [P0] Create DetectionResponseData model
  - id: str (request ID)
  - timestamp: datetime (ISO 8601)
  - version: str (default "1.0")
  - results: List[FieldDetectionResult]
  - processing_time_ms: int
  - **Acceptance**: Response can be JSON serialized

- [ ] **SCHEMA-4** [P0] Create ErrorResponse model
  - error.code: str (machine-readable error code)
  - error.message: str (human-readable)
  - error.request_id: str (for correlation)
  - **Acceptance**: Error response structure validated

- [ ] **SCHEMA-5** [P0] Create HealthResponse model
  - status: str ("healthy" or "unhealthy")
  - timestamp: datetime
  - version: str
  - checks: Dict[str, str] (component health)
  - **Acceptance**: Health response structure validated

## Service Layer - PDF Processing

- [ ] **PDF-SERVICE-1** [P0] Create PDFProcessingService class
  - Initialize with logger
  - Add class constants: MAX_FILE_SIZE, ALLOWED_MIME_TYPES, PDF_MAGIC_BYTES
  - **Acceptance**: Service instantiates

- [ ] **PDF-SERVICE-2** [P0] Implement validate_upload() method
  - Check file size < 50MB
  - Check MIME type is application/pdf
  - Check magic bytes (%PDF header)
  - Return (is_valid, error_message) tuple
  - **Acceptance**: Method returns correct validation results

- [ ] **PDF-SERVICE-3** [P0] Implement PDF parsing with pdfplumber
  - Read uploaded file bytes
  - Parse with pdfplumber
  - Extract pages, objects, text content
  - Build PDFDocument structure
  - Handle parsing errors gracefully
  - **Acceptance**: Can parse test PDFs and extract structure

- [ ] **PDF-SERVICE-4** [P0] Add error handling
  - Raise PDFValidationError for invalid files
  - Raise FileTooLargeError for oversized files
  - Raise PDFParsingError for parse failures
  - All inherit from base PDFProcessingError
  - **Acceptance**: Exceptions can be caught and handled

## Service Layer - Detector Integration

- [ ] **DETECTOR-SERVICE-1** [P0] Create DetectorService class
  - Constructor accepts Detector instance
  - Initialize with logger
  - **Acceptance**: Service instantiates with detector

- [ ] **DETECTOR-SERVICE-2** [P0] Implement detect_fields() method
  - Accept: document, fields, request_id
  - Create DetectionRequest for 2603-001 detector
  - Call detector.detect()
  - Map results to API schema
  - Return DetectionResponse
  - **Acceptance**: Method returns formatted response

- [ ] **DETECTOR-SERVICE-3** [P0] Add error handling
  - Raise DetectorError if detector fails
  - Include request_id in error logs
  - Timeout handling (5s limit)
  - **Acceptance**: Detector errors caught and logged

## Middleware & Logging

- [ ] **MIDDLEWARE-1** [P0] Create logging middleware
  - Capture request: method, path, headers
  - Measure response time
  - Generate request ID (UUID)
  - Log as structured JSON
  - Include response status code
  - **Acceptance**: Middleware logs correct format

- [ ] **MIDDLEWARE-2** [P0] Add request ID to response headers
  - Middleware sets "X-Request-ID" header
  - Request ID available in route handlers
  - **Acceptance**: Request ID visible in response headers

- [ ] **MIDDLEWARE-3** [P0] Create global exception handler
  - Catch all exceptions
  - Format as ErrorResponse JSON
  - Include request ID
  - Log with level = ERROR
  - **Acceptance**: Unhandled exceptions return 500 JSON

## REST Endpoints - Detection

- [ ] **ENDPOINT-DETECT-1** [P0] Implement POST /api/v1/detect
  - Accept file (multipart form)
  - Accept fields (optional query parameter, comma-separated)
  - Validate multipart data
  - Call PDFProcessingService.validate_upload()
  - Call PDFProcessingService.parse_pdf()
  - Call DetectorService.detect_fields()
  - Return DetectionResponseData with 200 OK
  - **Acceptance**: Endpoint accepts PDF and returns results

- [ ] **ENDPOINT-DETECT-2** [P0] Add error handling to /detect
  - 400 Bad Request: invalid PDF, no file, bad fields
  - 408 Request Timeout: detection takes > 5 seconds
  - 413 Payload Too Large: file > 50MB
  - 500 Internal Server Error: unexpected errors
  - All return structured ErrorResponse
  - **Acceptance**: Error scenarios return correct status + error JSON

- [ ] **ENDPOINT-DETECT-3** [P0] Add request timeout handling
  - Set timeout on detector.detect() call
  - Catch TimeoutError
  - Return 408 with error message
  - Log timeout as warning
  - **Acceptance**: Timeout returns 408 quickly

- [ ] **ENDPOINT-DETECT-4** [P0] Measure and log processing time
  - Start timer before detection
  - Calculate elapsed time in milliseconds
  - Include in response (processing_time_ms)
  - Include in request log
  - **Acceptance**: Processing time appears in response + logs

## REST Endpoints - Health

- [ ] **ENDPOINT-HEALTH-1** [P0] Implement GET /health
  - Check detector is accessible
  - Check PDF parser is accessible
  - Return HealthResponse with component statuses
  - Return 200 OK if healthy
  - Return 503 Service Unavailable if unhealthy
  - **Acceptance**: Endpoint returns correct health status

- [ ] **ENDPOINT-HEALTH-2** [P0] Add startup verification
  - On app startup, initialize detector
  - Verify detector is callable
  - Log startup status
  - Fail fast if detector unavailable
  - **Acceptance**: Startup completes successfully

## OpenAPI & Documentation

- [ ] **OPENAPI-1** [P0] Auto-generate OpenAPI schema
  - FastAPI auto-generates from docstrings + type hints
  - Verify schema at /openapi.json
  - **Acceptance**: OpenAPI schema is valid

- [ ] **OPENAPI-2** [P0] Add docstrings to endpoints
  - POST /detect: description, parameters, responses, examples
  - GET /health: description and responses
  - **Acceptance**: Swagger UI (/docs) shows documentation

- [ ] **OPENAPI-3** [P0] Document error responses
  - 400: example with INVALID_PDF_FORMAT error
  - 408: example with DETECTION_TIMEOUT
  - 413: example with PDF_TOO_LARGE
  - 500: example with DETECTOR_ERROR
  - **Acceptance**: Swagger UI shows error examples

## Unit Tests - Schemas

- [ ] **TEST-SCHEMA-1** [P0] Test DetectionRequest validation
  - Valid request with file + fields
  - Valid request with file only (defaults to ["signature", "initials"])
  - Invalid: fields with special characters
  - **Acceptance**: Valid requests accepted, invalid rejected

- [ ] **TEST-SCHEMA-2** [P0] Test response models
  - FieldDetectionResult with various confidences
  - DetectionResponseData with multiple results
  - JSON serialization roundtrip
  - **Acceptance**: Models serialize/deserialize correctly

- [ ] **TEST-SCHEMA-3** [P0] Test error response
  - ErrorResponse with all required fields
  - JSON serialization
  - **Acceptance**: Error response format correct

## Unit Tests - Services

- [ ] **TEST-PDF-SERVICE-1** [P0] Test PDF validation
  - Valid PDF: returns (True, None)
  - Too large (>50MB): returns (False, message)
  - Wrong MIME type: returns (False, message)
  - Wrong magic bytes: returns (False, message)
  - **Acceptance**: Validation works for all scenarios

- [ ] **TEST-PDF-SERVICE-2** [P0] Test PDF parsing
  - Parse simple test PDF
  - Extract pages, objects, content
  - Build valid PDFDocument structure
  - **Acceptance**: Can parse and structure PDF data

- [ ] **TEST-PDF-SERVICE-3** [P0] Test detector service integration
  - Call with mock detector
  - Verify results formatted correctly
  - Verify processing time included
  - **Acceptance**: Service returns formatted response

## Integration Tests - Endpoints

- [ ] **TEST-ENDPOINT-DETECT-1** [P0] Test POST /detect success
  - Upload valid PDF
  - Specify fields
  - Verify 200 OK response
  - Verify response has id, timestamp, results, processing_time_ms
  - **Acceptance**: Endpoint returns complete response

- [ ] **TEST-ENDPOINT-DETECT-2** [P0] Test POST /detect with defaults
  - Upload PDF without fields parameter
  - Verify default fields used
  - **Acceptance**: Defaults applied correctly

- [ ] **TEST-ENDPOINT-DETECT-3** [P0] Test POST /detect error scenarios
  - No file uploaded: 400
  - Non-PDF file: 400
  - Invalid fields: 400
  - **Acceptance**: Error scenarios return correct status

- [ ] **TEST-ENDPOINT-HEALTH-1** [P0] Test GET /health endpoint
  - Call /health
  - Verify 200 OK
  - Verify response has status, checks, version
  - **Acceptance**: Health endpoint works

- [ ] **TEST-ENDPOINT-HEALTH-2** [P0] Test health check format
  - Verify checks include detector, pdf_parser
  - Verify each check has value
  - **Acceptance**: Health check response complete

## Integration Tests - Full Flow

- [ ] **TEST-INTEGRATION-1** [P0] End-to-end happy path
  - Create test PDF with signature field
  - POST /detect with PDF
  - Verify detection results
  - Check all fields populated
  - **Acceptance**: Full round-trip works

- [ ] **TEST-INTEGRATION-2** [P0] End-to-end error handling
  - Submit bad file
  - Verify error response format
  - Verify request ID in error
  - Log error appropriately
  - **Acceptance**: Error handling works end-to-end

- [ ] **TEST-INTEGRATION-3** [P0] Concurrent requests
  - Send 10 concurrent requests
  - Verify all complete successfully
  - Verify unique request IDs
  - **Acceptance**: Concurrent requests handled

## Performance & Load

- [ ] **PERF-1** [P0] Measure latency
  - Single request latency: < 2 seconds
  - Measure P50, P95, P99
  - Log slow requests (> 1s)
  - **Acceptance**: Latency meets SLA

- [ ] **PERF-2** [P0] Test with large PDFs
  - Create 50MB test PDF
  - Verify returns 413 Payload Too Large
  - **Acceptance**: Size limit enforced

- [ ] **PERF-3** [P0] Measure memory usage
  - Monitor memory during requests
  - Verify cleanup after requests
  - **Acceptance**: No memory leaks detected

## Testing Coverage & Quality

- [ ] **COVERAGE-1** [P0] Run full test suite
  - Command: `pytest -v tests/`
  - All tests passing
  - **Acceptance**: 100% of tests pass

- [ ] **COVERAGE-2** [P0] Generate coverage report
  - Command: `pytest --cov=api tests/`
  - Target: >= 80% coverage
  - **Acceptance**: Coverage report shows >= 80%

- [ ] **COVERAGE-3** [P0] Type checking
  - Command: `mypy api --strict`
  - Fix all type errors
  - **Acceptance**: mypy passes

- [ ] **COVERAGE-4** [P0] Linting
  - Command: `pylint api`
  - Command: `flake8 api`
  - Fix critical issues
  - **Acceptance**: Linting passes

## Documentation

- [ ] **DOCS-1** [P0] Write API README
  - Overview of endpoints
  - Quick start example
  - Error codes documentation
  - **Acceptance**: README is clear

- [ ] **DOCS-2** [P0] Create curl examples
  - Example: POST /detect with file
  - Example: GET /health
  - Example: Error response
  - Save to docs/examples/
  - **Acceptance**: Examples are runnable

- [ ] **DOCS-3** [P0] Document configuration
  - Port configuration
  - Detector selection
  - Logging level configuration
  - **Acceptance**: Configuration documented

## Docker & Deployment

- [ ] **DOCKER-1** [P0] Create Dockerfile
  - Base: python:3.11-slim
  - Install dependencies from requirements.txt
  - Copy app code
  - Expose port 8000
  - CMD: uvicorn api.main:app
  - **Acceptance**: Docker image builds

- [ ] **DOCKER-2** [P0] Build and test Docker image
  - Build image: `docker build -t sig-detect:latest .`
  - Run container: `docker run -p 8000:8000 sig-detect:latest`
  - Test GET /health
  - **Acceptance**: Container runs and responds

- [ ] **DOCKER-3** [P0] Create requirements.txt
  - FastAPI
  - uvicorn
  - pydantic
  - pdfplumber
  - pytest (dev)
  - **Acceptance**: `pip install -r requirements.txt` works

## Build & Package

- [ ] **BUILD-1** [P0] Add setup.py or pyproject.toml
  - Package metadata
  - Version: 1.0.0 (MVP)
  - **Acceptance**: Package structure valid

- [ ] **BUILD-2** [P0] Create Makefile (optional)
  - `make test`: run tests
  - `make coverage`: generate coverage
  - `make docker`: build Docker image
  - **Acceptance**: Make targets work

## Sign-Off & Handoff

- [ ] **FINAL-1** [P0] Code review checklist
  - All tests passing
  - Coverage >= 80%
  - Type checking passes
  - Linting passes
  - Documentation complete
  - Docker image builds and runs
  - **Acceptance**: All checklist items verified

- [ ] **FINAL-2** [P0] Integration with 2603-001
  - 2603-001 module imported correctly
  - Detector instantiation works
  - Results correctly formatted
  - No dependency conflicts
  - **Acceptance**: API and detector work together

- [ ] **FINAL-3** [P0] Create deployment guide
  - How to run locally
  - How to deploy to Docker
  - Environment variables
  - Health check verification
  - **Acceptance**: Guide is clear

- [ ] **FINAL-4** [P0] Handoff to ops/deployment
  - Docker image tagged and documented
  - Health check endpoint verified
  - Metrics/logging explained
  - Known issues documented
  - **Acceptance**: Ready for deployment

## Effort Estimate

| Phase | Tasks | Est. Effort | Notes |
|-------|-------|-------------|-------|
| Setup | SETUP-1, SETUP-2 | 0.5 days | Project scaffolding |
| Schemas | SCHEMA-1 to SCHEMA-5 | 1 day | Pydantic models |
| Services | PDF-SERVICE-1 to PDF-SERVICE-4, DETECTOR-SERVICE-1 to DETECTOR-SERVICE-3 | 1.5 days | Core logic |
| Middleware | MIDDLEWARE-1 to MIDDLEWARE-3 | 0.5 days | Logging & exception handling |
| Endpoints | ENDPOINT-DETECT-1 to ENDPOINT-DETECT-4, ENDPOINT-HEALTH-1 to ENDPOINT-HEALTH-2 | 1.5 days | Route implementations |
| OpenAPI | OPENAPI-1 to OPENAPI-3 | 0.5 days | Documentation |
| Unit Tests | TEST-SCHEMA-1 to TEST-SCHEMA-3, TEST-PDF-SERVICE-1 to TEST-PDF-SERVICE-3 | 1.5 days | Service testing |
| Integration | TEST-ENDPOINT-DETECT-1 to TEST-ENDPOINT-DETECT-3, TEST-ENDPOINT-HEALTH-1 to TEST-ENDPOINT-HEALTH-2, TEST-INTEGRATION-1 to TEST-INTEGRATION-3 | 2 days | End-to-end tests |
| Performance | PERF-1 to PERF-3 | 0.5 days | Performance validation |
| Coverage | COVERAGE-1 to COVERAGE-4 | 0.5 days | Quality gates |
| Documentation | DOCS-1 to DOCS-3 | 0.5 days | Guides and examples |
| Docker | DOCKER-1 to DOCKER-3 | 1 day | Containerization |
| Build | BUILD-1 to BUILD-2 | 0.25 days | Packaging |
| Sign-Off | FINAL-1 to FINAL-4 | 0.5 days | Review + handoff |
| **TOTAL** | **28 tasks** | **~12-14 days** | **1-2 developers** |

## Success Criteria (Definition of Done)

- [x] All 28 tasks completed and verified
- [x] All tests passing (`pytest -v`)
- [x] Coverage report shows >= 80%
- [x] Type checking passes (`mypy --strict`)
- [x] Linting passes (`pylint api/`)
- [x] Docker image builds and runs
- [x] Health check verified
- [x] Code review approved
- [x] Documentation complete and reviewed
- [x] Ready for deployment
