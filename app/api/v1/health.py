import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.health import DatabaseHealth, HealthCheckResponse

router = APIRouter()


def perform_health_check(db: Session) -> tuple[HealthCheckResponse, int]:
    """
    Checks database connectivity using SELECT 1 and returns the health schema and status code.
    Returns (HealthCheckResponse, 200) if healthy, or (HealthCheckResponse, 503) if database is unreachable.
    """
    now = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        health_data = HealthCheckResponse(
            status="healthy",
            timestamp=now,
            environment=settings.ENVIRONMENT,
            database=DatabaseHealth(
                status="connected",
                latency_ms=latency_ms,
            ),
        )
        return health_data, status.HTTP_200_OK
    except Exception as e:
        health_data = HealthCheckResponse(
            status="unhealthy",
            timestamp=now,
            environment=settings.ENVIRONMENT,
            database=DatabaseHealth(
                status="disconnected",
                error=str(e),
            ),
        )
        return health_data, status.HTTP_503_SERVICE_UNAVAILABLE


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check service status and database connectivity.",
    responses={
        200: {
            "description": "Service and database are healthy",
            "model": HealthCheckResponse,
        },
        503: {
            "description": "Service or database is unhealthy",
            "model": HealthCheckResponse,
        },
    },
)
def health_check(response: Response, db: Session = Depends(get_db)) -> HealthCheckResponse:
    data, status_code = perform_health_check(db)
    response.status_code = status_code
    return data

