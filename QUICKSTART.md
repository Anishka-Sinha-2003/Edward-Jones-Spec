# Implementation Quickstart Guide

> 🚀 **Ready to code?** Start here.

This guide provides everything needed to begin implementing the signature detection service. All specs, designs, and tasks are complete. This is a spec-driven project—implementation follows design.

## 5-Minute Overview

**Goal**: Build a service that detects signatures in PDFs + returns JSON with confidence scores via REST API.

**Two Independent Specs** (can work in parallel):

1. **2603-001: Signature Detection Core** (7-8 days)
   - What: Python module with mock detector
   - Input: PDF document + field names
   - Output: status (present/absent/uncertain) + confidence (0-1)
   - Tests: >80% coverage
   - Result: `src/signature_detection/` importable module

2. **2603-002: REST API Integration** (12-14 days, requires 2603-001 first)
   - What: FastAPI endpoints to call detector
   - Endpoints: `POST /api/v1/detect` + `GET /health`
   - Tests: >80% coverage
   - Docker: Image that runs and responds
   - Result: Production-ready REST service

**Tech Stack**:
- Python 3.11
- FastAPI (web framework)
- pdfplumber (PDF parsing)
- pytest (testing)
- Docker (deployment)

## Step 1: Pick Your Starting Spec

### Option A: Build the Core (2603-001)

Start with the detection module. Best if:
- You're strong with Python + testing
- You want to unblock the API team
- You prefer unit testing + algorithms

**Start here**: [2603-001-signature-detection-core/](specs/2603-001-signature-detection-core/)

### Option B: Build the API (2603-002)

Start with REST endpoints. Best if:
- You know FastAPI / web frameworks well
- 2603-001 is already mostly done
- You prefer integration testing + HTTP

**Start here**: [2603-002-api-integration/](specs/2603-002-api-integration/)

**⚠️ Note**: 2603-002 requires 2603-001 complete first.

---

## Option A: 2603-001 Quickstart

### 📋 Read These (30 min)

1. [specs/constitution.md](specs/constitution.md) - Non-negotiable standards
2. [specs/../.architecture/architecture.md](specs/.architecture/architecture.md) - Tech decisions
3. [specs/2603-001-signature-detection-core/spec.md](specs/2603-001-signature-detection-core/spec.md) - What you're building
4. [specs/2603-001-signature-detection-core/design.md](specs/2603-001-signature-detection-core/design.md) - How to build it

### 🛠️ Setup Project (15 min)

```bash
# Create directories
mkdir -p src/signature_detection/{detectors}
mkdir -p tests/fixtures

# Initialize Python project
cd d:\Edward\ Jones\Edward-Jones-Spec
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install pytest pytest-cov mypy pylint flake8 pydantic

# Create requirements.txt
pip freeze > requirements.txt
```

### 📝 Implement (7-8 days)

Follow [2603-001-signature-detection-core/tasks.md](specs/2603-001-signature-detection-core/tasks.md):

**Week 1**:
- [ ] Tasks SETUP-1 through DETECTOR-2 (structure + base class)
- [ ] Tasks MOCK-DETECT-1 through MOCK-DETECT-4 (implementation)
- [ ] Tasks SCORE-1 through SCORE-2 (confidence scoring)
- [ ] Tasks VALIDATE-1 through VALIDATE-2 (validation)

**Week 2**:
- [ ] Tasks TEST-* (all unit tests)
- [ ] Tasks FIXTURES-* (test data)
- [ ] Tasks DOCS-* (documentation)
- [ ] Tasks INTEGRATION-* (wire up for API)
- [ ] Tasks BUILD-* (packaging)
- [ ] Tasks FINAL-* (review & sign-off)

### 🧪 Test & Verify (Continuous)

```bash
# After each task
pytest -v tests/
pytest --cov=src/signature_detection tests/
mypy src/signature_detection --strict
pylint src/signature_detection
flake8 src/signature_detection
```

### ✅ Sign-Off

When all tasks done:
- [ ] Tests pass: `pytest -v tests/`
- [ ] Coverage ≥80%: `pytest --cov=src tests/ --cov-fail-under=80`
- [ ] Type checking: `mypy src/signature_detection --strict` (0 errors)
- [ ] Linting: `pylint src/` + `flake8 src/` (clean)
- [ ] Documentation: README + docstrings complete
- [ ] Ready for 2603-002 API integration

---

## Option B: 2603-002 Quickstart

### 📋 Read These (30 min)

1. [specs/constitution.md](specs/constitution.md) - Standards
2. [specs/.architecture/architecture.md](specs/.architecture/architecture.md) - Tech stack
3. [specs/2603-002-api-integration/spec.md](specs/2603-002-api-integration/spec.md) - API contract
4. [specs/2603-002-api-integration/design.md](specs/2603-002-api-integration/design.md) - Design + code examples

### 🛠️ Setup Project (15 min)

```bash
# Requires: 2603-001 module complete and importable
# Create directories
mkdir -p api/{routes,schemas,services,middleware}
mkdir -p tests/
mkdir -p infra/

# Activate venv (from 2603-001)
cd d:\Edward\ Jones\Edward-Jones-Spec
venv\Scripts\activate

# Install additional dependencies
pip install fastapi uvicorn pdfplumber

# Update requirements.txt
pip freeze > requirements.txt
```

### 📝 Implement (12-14 days)

Follow [2603-002-api-integration/tasks.md](specs/2603-002-api-integration/tasks.md):

**Week 2 (in parallel with 2603-001 if possible)**:
- [ ] Tasks SETUP-1 through SETUP-2 (project structure)
- [ ] Tasks SCHEMA-1 through SCHEMA-5 (Pydantic models)
- [ ] Tasks PDF-SERVICE-1 through DETECTOR-SERVICE-3 (business logic)

**Week 3**:
- [ ] Tasks MIDDLEWARE-* (logging + error handling)
- [ ] Tasks ENDPOINT-DETECT-* + ENDPOINT-HEALTH-* (REST endpoints)
- [ ] Tasks OPENAPI-* (documentation)
- [ ] Tasks TEST-* (unit + integration tests)

**Week 4**:
- [ ] Tasks PERF-* (performance validation)
- [ ] Tasks COVERAGE-* (quality gates)
- [ ] Tasks DOCS-* (deployment guide)
- [ ] Tasks DOCKER-* (containerization)
- [ ] Tasks BUILD-* (packaging)
- [ ] Tasks FINAL-* (sign-off)

### 🧪 Test & Verify (Continuous)

```bash
# Start app
uvicorn api.main:app --reload

# In another terminal, test it
curl -X GET http://localhost:8000/health

# Run tests
pytest -v tests/
pytest --cov=api tests/
mypy api --strict
pylint api
```

### 🐳 Docker (Week 4)

```bash
# Build image
docker build -t sig-detect:latest .

# Run container
docker run -p 8000:8000 sig-detect:latest

# Test
curl http://localhost:8000/health
```

### ✅ Sign-Off

When all tasks done:
- [ ] Tests pass: `pytest -v tests/`
- [ ] Coverage ≥80%: `pytest --cov=api tests/ --cov-fail-under=80`
- [ ] Type checking: `mypy api --strict` (0 errors)
- [ ] Linting: `pylint api/` + `flake8 api/` (clean)
- [ ] Docker: Image builds + health check works
- [ ] API works end-to-end: upload PDF → get results

---

## Project Essentials

### Key Files to Know

```
specs/
├── constitution.md                    ← Read first: quality standards
├── .project-plan/
│   ├── charter.md                     ← Project goals & risks
│   └── project-plan.md                ← Spec catalog & timeline
├── .architecture/
│   └── architecture.md                ← Tech decisions (C4 diagrams, ADRs)
├── 2603-001-signature-detection-core/
│   ├── spec.md                        ← Requirements (read before coding)
│   ├── design.md                      ← Architecture + algorithms
│   └── tasks.md                       ← Checklist of 24 tasks
└── 2603-002-api-integration/
    ├── spec.md                        ← API contracts (endpoints, JSON)
    ├── design.md                      ← FastAPI design + examples
    └── tasks.md                       ← Checklist of 28 tasks
```

### Design Documents Are Your Map

Each spec has three docs:
1. **spec.md** = "What are we building?" (business view)
2. **design.md** = "How do we build it?" (architecture + pseudocode)
3. **tasks.md** = "Who does what, in what order?" (checklist + estimation)

**Use them in order**: Read spec → review design → execute tasks.

---

## Make Decisions Visible

Each spec has **open questions** in the frontmatter. If you encounter decisions not covered:

1. Check the design.md for ADRs (Architecture Decision Records)
2. Check the [constitution.md](specs/constitution.md) for standards
3. If still unclear, document your decision in the spec frontmatter
4. Get reviewed before merging

---

## Code Quality Non-Negotiables

(From [constitution.md](specs/constitution.md))

- **Tests**: ≥80% coverage (enforced by CI)
- **Types**: mypy --strict (all types explicit)
- **Lint**: pylint + flake8 (code style)
- **Docs**: Docstrings on all public APIs
- **Logging**: Structured JSON logging

**Why?** These aren't cosmetic—they affect:
- Reliability (tests catch regressions)
- Maintainability (types + docs prevent bugs)
- Observability (JSON logs enable monitoring)

---

## Parallel Work

**Can 2603-001 & 2603-002 happen in parallel?**

Sort of. 2603-002 needs 2603-001's detector interface. So:
- **Weeks 1-2**: 2603-001 design + implementation (in progress)
- **Week 2**: 2603-002 design (read-only dependency on 2603-001 spec)
- **Week 2-3**: 2603-002 implementation (waits for 2603-001 code)

Ideal: 2603-001 complete by end of Week 2, so 2603-002 can go full-speed Weeks 3-4.

---

## Getting Unblocked

**Question**: Where's the answer?

| Question | First Look | Second Look |
|----------|-----------|------------|
| "What am I building?" | spec.md | design.md examples |
| "How do I design this?" | design.md | ADR in .architecture/ |
| "What code do I write first?" | tasks.md | task acceptance criteria |
| "What tests do I need?" | design.md test section | tasks.md test tasks |
| "What's the quality bar?" | constitution.md | design.md quality section |
| "How do I structure dirs?" | design.md class diagram | design.md module organization |
| "How do I deploy?" | DOCKER-* tasks | design.md deployment section |

**Stuck?** Check the design.md signature section for your topic, then expand to related specs.

---

## Success = Declaration

When you're truly done:

```bash
# 2603-001 sign-off
git log --oneline | head -30  # Shows ~24 commits (one per task)
pytest --cov=src --cov-report=term-missing  # ≥80%
mypy src/signature_detection --strict  # 0 errors
pylint src/signature_detection  # No criticals
flake8 src/signature_detection  # Clean
# → Ready for code review

# 2603-002 sign-off
git log --oneline | head -50  # Shows ~28 commits
pytest --cov=api --cov-report=term-missing  # ≥80%
mypy api --strict  # 0 errors
pylint api  # No criticals
flake8 api  # Clean
docker run -p 8000:8000 sig-detect:latest  # Runs
curl http://localhost:8000/health  # Returns 200
# → Ready for deployment
```

Sounds right? Then you're done.

---

## Final Checklist

Before you start coding:

- [ ] You've read constitution.md (standards)
- [ ] You've read .architecture/architecture.md (decisions)
- [ ] You've picked which spec (2603-001 or 2603-002)
- [ ] You've read that spec's spec.md (requirements)
- [ ] You've read that spec's design.md (architecture)
- [ ] You've created the directory structure
- [ ] You've set up your Python environment
- [ ] You have pytest, mypy, pylint, flake8 installed
- [ ] You've got test files open in your editor
- [ ] Your team knows what you're building

Go build something great! 🚀

---

**Questions?** Check specs first. They're complete and detailed. If something's still unclear, that's a gap to document and fix.

**Stuck on a task?** Review that task's acceptance criteria in tasks.md. It defines exactly what "done" looks like.

---

Coded with AIS-spec
