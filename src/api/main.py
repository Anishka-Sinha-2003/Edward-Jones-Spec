"""
FastAPI Application Entry Point

Main application factory and configuration.
Spec: 2603-002 REST API Integration
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, detect


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown lifecycle handler.
    """
    # Startup
    logger.info("🚀 Signature Detection API starting up...")
    logger.info(f"⏰ Started at {datetime.now().isoformat()}")

    yield

    # Shutdown
    logger.info("🛑 Signature Detection API shutting down...")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="Signature Detection API",
        description="REST API for detecting signatures in PDF documents",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS Middleware (minimal for MVP)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    logger.info("📝 Registering routes...")
    app.include_router(health.router, tags=["Health"])
    app.include_router(detect.router, tags=["Detection"])

    logger.info("✅ Application configured successfully")

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    """
    Local development server.

    Run with:
        python api/main.py

    Or with uvicorn:
        uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    """
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
