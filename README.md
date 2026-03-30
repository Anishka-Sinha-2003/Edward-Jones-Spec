# Edward Jones — Signature & Initial Detection (MVP)

Spec-driven MVP for a **signature and initial detection** service: a Python detection core (**2603-001**), a **FastAPI** REST layer with **real PDF upload** (**2603-002**), and a **light-themed web UI** for demos and manual checks.

This repository is a **foundation** for the full engagement described in the client Statement of Work (SOW). The SOW targets vision-based detection, Edward Jones document templates (IAP/CAP), Azure deployment, and a quality framework; those items are **not fully implemented here**—see [Alignment with the SOW](#alignment-with-the-sow) below.

---

## What is implemented today

| Area | Status |
|------|--------|
| **Detection core** (`src/signature_detection/`) | `Detector` ABC, **`MockDetector`** (heuristic, field-name patterns), models, scoring, validators |
| **REST API** (`src/api/`) | **`POST /api/v1/detect`** — multipart PDF + optional `fields`; **`GET /health`**; structured JSON errors + **`X-Request-ID`** |
| **PDF handling** | Validation (magic bytes, 50 MB limit), **`pdfplumber`** parse → internal `PDFDocument` |
| **Web UI** (`frontend/`) | Upload form, human-readable results (status, confidence bar), optional technical JSON; served at **`/ui/`** ( **`/`** redirects) |
| **OpenAPI** | **`/docs`**, **`/openapi.json`** (FastAPI) |
| **Tests** | `pytest` + `tests/api/test_detect_upload.py` (multipart flow); core tests under `tests/` |
| **Container** | `infra/Dockerfile` (Python 3.11, `PYTHONPATH=/app/src`) |

---

## Repository layout

```
Edward-Jones-Spec/
├── .project-context/          # Gitignored locally — SOW, RFPs, etc. (not committed by default)
├── frontend/                  # Static UI (index.html, styles.css, app.js)
├── infra/
│   └── Dockerfile
├── specs/
│   ├── 2603-001-signature-detection-core/   # Core spec, design, tasks
│   ├── 2603-002-api-integration/            # API spec, design, tasks
│   ├── .architecture/
│   ├── .project-plan/
│   └── constitution.md
├── src/
│   ├── api/                   # FastAPI app
│   │   ├── main.py
│   │   ├── exceptions.py
│   │   ├── middleware/
│   │   ├── routes/            # detect.py, health.py
│   │   ├── schemas/
│   │   └── services/          # pdf_processing, detector_service
│   └── signature_detection/   # Core library
├── tests/
│   ├── api/
│   └── conftest.py
├── examples/
│   ├── run_mock_detector.py
│   └── test_detect_endpoint.py
├── pytest.ini
├── requirements.txt
├── CONTRIBUTING.md
└── README.md
```

---

## Prerequisites

- **Python 3.11** recommended (matches Docker; pinned dependencies have reliable wheels).
- **Python 3.13** may require building some packages from source unless you use newer unpinned versions.

Install dependencies:

```bash
cd "d:\Edward Jones\Edward-Jones-Spec"
python -m pip install -r requirements.txt
```

Key packages: **FastAPI**, **uvicorn**, **python-multipart** (file uploads), **pdfplumber**, **pydantic**, **pytest**, **httpx**, **pypdf** (test PDF generation).

---

## Run the API and web UI

The `api` package must be on **`PYTHONPATH`**, or run from **`src`** so imports resolve.

**Option A — from `src` (simplest on Windows):**

```bat
cd "d:\Edward Jones\Edward-Jones-Spec\src"
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Option B — from repo root:**

```bat
cd "d:\Edward Jones\Edward-Jones-Spec"
set PYTHONPATH=src
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/ | Redirects to the UI |
| http://127.0.0.1:8000/ui/ | Upload PDF and view results |
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/health | Health check JSON |

**Example (curl):**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/detect ^
  -F "file=@path\to\document.pdf" ^
  -F "fields=signature_field_1,initials"
```

---

## API summary (spec 2603-002)

### `POST /api/v1/detect`

- **Content-Type:** `multipart/form-data`
- **Form fields:**
  - **`file`** (required): PDF binary
  - **`fields`** (optional): comma-separated field names; default behavior uses common defaults if omitted
- **Success (200):** `id`, `timestamp`, `version`, `results[]` (`field_name`, `status`, `confidence`, `metadata`), `processing_time_ms`
- **Errors:** JSON body `{ "error": { "code", "message", "request_id" } }` with appropriate HTTP status (e.g. 400, 413, 408, 500)

### `GET /health`

Returns service and dependency status (detector import, pdfplumber availability).

---

## Run core-only example (no HTTP)

```bash
cd "d:\Edward Jones\Edward-Jones-Spec"
python examples/run_mock_detector.py
```

Uses `MockDetector` on a synthetic in-memory document (useful for understanding the core module).

---

## Tests

```bash
cd "d:\Edward Jones\Edward-Jones-Spec"
python -m pytest tests/ -v
```

`pytest.ini` sets `pythonpath = src`. API tests use **pypdf** to build minimal PDF bytes.

---

## Docker

From the repository root (adjust image name/tag as needed):

```bash
docker build -f infra/Dockerfile -t signature-detection-api .
docker run --rm -p 8000:8000 signature-detection-api
```

The image sets `PYTHONPATH=/app/src` and runs `uvicorn api.main:app`.

---

## Specifications

| Spec | Path | Focus |
|------|------|--------|
| **2603-001** | `specs/2603-001-signature-detection-core/` | Models, `Detector`, mock implementation |
| **2603-002** | `specs/2603-002-api-integration/` | REST contract, PDF upload, errors, health |

Project-level planning and architecture: `specs/.project-plan/`, `specs/.architecture/`, `specs/constitution.md`.

---

## Alignment with the SOW

The SOW (see `.project-context/` when present) describes **Edward Jones document types** (IAP/CAP forms), **300 DPI / 8×11** parameters, **vision-based** detection (e.g. GPT-4 Vision), **template zones**, **document-level flagging**, **French variants**, **Azure** deployment, and an **accuracy / drift** framework.

**This repo today:**

- Delivers a **synchronous REST** surface and **real PDF upload** consistent with the integration *pattern* in the SOW.
- Uses **`MockDetector`**, not production vision or per-form templates.
- Does **not** validate DPI/page size against SOW limits, classify form IDs, or deploy to client Azure.

Treat this codebase as the **MVP spine**; full SOW compliance is tracked in later specs/phases (e.g. real detector integration, template configuration, Azure, analytics).

---

## Contributing

See **`CONTRIBUTING.md`** for conventions, branching, and review expectations.

---

## Additional documentation

- `QUICKSTART.md` — Broader implementation quickstart
- `docs/API-SETUP-GUIDE.md`, `docs/DETECT-ENDPOINT.md` — API notes (may predate latest UI; prefer this README + `/docs`)
- `MOCK-DETECT-WALKTHROUGH.md`, `SETUP-1-WALKTHROUGH.md` — Deeper walkthroughs

---

## License / confidentiality

Client SOW and materials under `.project-context/` are confidential. Do not commit secrets or client-only artifacts unless your process explicitly allows it.
