"""Pydantic schemas for the health endpoint."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body returned by GET /health."""

    status: str
    timestamp: str