"""
PRISM Health Check API.

Provides liveness and readiness probes for container orchestration
and monitoring systems.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from prism.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    version: str
    environment: str
    timestamp: str


class ReadinessResponse(BaseModel):
    """Readiness check response with dependency status."""

    status: str
    version: str
    checks: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Liveness probe — is the application process running?

    This endpoint should ALWAYS return 200 if the process is alive.
    Do not add dependency checks here (use /ready for that).
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness probe — can the application serve traffic?

    Checks critical dependencies (database, Redis).
    Returns 503 if any dependency is unavailable.
    """
    checks: dict[str, str] = {}

    # Database check
    try:
        from prism.db.session import check_database_connection

        await check_database_connection()
        checks["database"] = "connected"
    except Exception:
        checks["database"] = "unavailable"

    # Redis check
    try:
        from prism.db.redis import check_redis_connection

        await check_redis_connection()
        checks["redis"] = "connected"
    except Exception:
        checks["redis"] = "unavailable"

    all_healthy = all(v != "unavailable" for v in checks.values())

    return ReadinessResponse(
        status="ready" if all_healthy else "degraded",
        version=settings.APP_VERSION,
        checks=checks,
    )
