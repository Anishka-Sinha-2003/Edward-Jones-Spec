"""Pydantic models for API responses (spec 2603-002)."""

from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class FieldDetectionResult(BaseModel):
    field_name: str = Field(..., description="Name of the field detected")
    status: str = Field(
        ...,
        description="Detection status: present, absent, uncertain",
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DetectionResponseData(BaseModel):
    id: str = Field(..., description="Unique request ID")
    timestamp: datetime = Field(..., description="Server timestamp (UTC)")
    version: str = Field(default="1.0", description="API version")
    results: List[FieldDetectionResult]
    processing_time_ms: int = Field(..., ge=0)


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponseModel(BaseModel):
    status: str
    timestamp: str
    version: str
    checks: Dict[str, str]
