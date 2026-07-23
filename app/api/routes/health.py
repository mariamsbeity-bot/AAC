"""Health check route."""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=200)
def get_health() -> HealthResponse:
    """Health check endpoint.

    Route:
        GET /health

    Returns:
        HealthResponse: ``status`` is always the literal ``"ok"``;
            ``timestamp`` is the current UTC time as an ISO 8601 string.

    Example:
        GET /health -> 200
        {"status": "ok", "timestamp": "2026-07-23T11:44:08.323789+00:00"}
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )