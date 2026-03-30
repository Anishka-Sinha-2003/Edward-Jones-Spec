"""
FastAPI Application Entry Point

Main application factory and configuration.
Spec: 2603-002 REST API Integration
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .exceptions import APIError
from .middleware.request_id import RequestIDMiddleware
from .routes import detect, health
from .schemas.responses import ErrorDetail, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Project root: src/api/main.py -> parent.parent.parent
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    logger.info("Signature Detection API starting up...")
    logger.info("Started at %s", datetime.now().isoformat())
    yield
    logger.info("Signature Detection API shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Signature Detection API",
        description="REST API for detecting signatures in PDF documents",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        body = ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                request_id=request_id,
            )
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=body.model_dump(mode="json"),
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    logger.info("Registering routes...")
    app.include_router(health.router, tags=["Health"])
    app.include_router(detect.router, tags=["Detection"])

    if FRONTEND_DIR.is_dir():

        @app.get("/", include_in_schema=False)
        async def root_to_ui() -> RedirectResponse:
            """Send browsers to the upload UI (mounted below /ui)."""
            return RedirectResponse(url="/ui/", status_code=302)

        app.mount(
            "/ui",
            StaticFiles(directory=str(FRONTEND_DIR), html=True),
            name="frontend",
        )
        logger.info("Serving frontend at /ui from %s", FRONTEND_DIR)
    else:
        logger.warning("No frontend/ directory found — UI not served")

    logger.info("Application configured successfully")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
