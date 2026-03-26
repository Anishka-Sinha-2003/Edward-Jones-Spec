# Project Constitution: Signature & Initial Detection Service

## Non-Negotiable Standards

### Code Quality
- **Testing**: Minimum 80% code coverage for detection logic
- **Type Safety**: Fully typed Python with mypy strict mode
- **Logging**: Structured JSON logging for all detection operations
- **Documentation**: All public APIs must have docstrings with examples

### Performance
- **PDF Processing**: Detection must complete within 5 seconds for typical documents
- **API Response Time**: P99 latency < 2 seconds for single document
- **Memory**: Peak memory usage must not exceed 500MB per concurrent request

### Reliability
- **Error Handling**: All exceptions caught and logged; graceful degradation for uncertain results
- **Validation**: Input validation on all PDF documents (size, format, content)
- **State**: Service must be stateless and horizontally scalable

### Signature Detection
- **Confidence Scoring**: All results must include 0-1 confidence score
- **Field Mapping**: Output JSON must always include field name, status, and confidence
- **Mocking**: Initial implementation can mock detection; must support real detection injection
- **Schema**: Response schema must be versioned and backward compatible

### API Standards
- **REST Compliance**: Endpoint must follow REST conventions
- **Error Responses**: Consistent error JSON with error codes and messages
- **Rate Limiting**: Support for rate limiting without code changes
- **Authentication**: Ready for auth integration (not required for MVP)

### Deployment & Operations
- **Containerization**: Must run in Docker
- **Health Checks**: `/health` endpoint required
- **Monitoring**: Prometheus metrics exported for signature detection latency and status counts
- **CI/CD**: All code changes must pass tests before merge

## Authority & Decision Tracking
- **Decisions**: Captured in ADRs in `.architecture/decisions/`
- **Backlog**: Open questions tracked in spec frontmatter with POC assignment
- **Review**: All specs require peer review before design phase
- **Status**: Updated weekly in project reports
