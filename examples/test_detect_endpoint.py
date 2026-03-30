"""
Test script: POST /api/v1/detect (multipart PDF upload).

Run the server from repo root with PYTHONPATH including `src`:

  set PYTHONPATH=src
  python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

Then open http://127.0.0.1:8000/ (redirects to /ui/) or use curl:

  curl -X POST http://127.0.0.1:8000/api/v1/detect ^
    -F "file=@path/to/sample.pdf" ^
    -F "fields=signature_field_1,initials"
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_endpoint_direct() -> bool:
    """Call route handler with a tiny PDF (requires pypdf)."""
    print("\n" + "=" * 70)
    print("Direct multipart-style test (in-memory PDF)")
    print("=" * 70)
    try:
        from io import BytesIO

        from pypdf import PdfWriter

        from api.routes.detect import detect_signatures
        from fastapi import UploadFile
        from unittest.mock import MagicMock

        w = PdfWriter()
        w.add_blank_page(width=612, height=792)
        buf = BytesIO()
        w.write(buf)
        pdf_bytes = buf.getvalue()

        upload = UploadFile(
            filename="sample.pdf",
            file=BytesIO(pdf_bytes),
        )

        req = MagicMock()
        req.state.request_id = "test-req-id"

        async def run():
            return await detect_signatures(
                request=req,
                file=upload,
                fields="signature_field_1,initials",
            )

        result = asyncio.run(run())
        out = result.model_dump(mode="json")
        print(json.dumps(out, indent=2, default=str))
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("POST /api/v1/detect — PDF upload (spec 2603-002)")
    ok = test_endpoint_direct()
    sys.exit(0 if ok else 1)
