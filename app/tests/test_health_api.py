from unittest.mock import MagicMock
from fastapi import Response, status
from app.api.v1.health import health_check, perform_health_check
from app.core.config import settings
from app.main import app
from app.schemas.health import HealthCheckResponse


def test_perform_health_check_success():
    mock_db = MagicMock()
    mock_db.execute.return_value = MagicMock()

    result, status_code = perform_health_check(mock_db)

    assert status_code == status.HTTP_200_OK
    assert isinstance(result, HealthCheckResponse)
    assert result.status == "healthy"
    assert result.environment == settings.ENVIRONMENT
    assert result.database.status == "connected"
    assert result.database.latency_ms is not None
    assert result.database.latency_ms >= 0
    assert result.database.error is None
    assert result.timestamp is not None
    mock_db.execute.assert_called_once()


def test_perform_health_check_db_failure():
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("Connection to PostgreSQL failed")

    result, status_code = perform_health_check(mock_db)

    assert status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert isinstance(result, HealthCheckResponse)
    assert result.status == "unhealthy"
    assert result.database.status == "disconnected"
    assert result.database.latency_ms is None
    assert "Connection to PostgreSQL failed" in result.database.error


def test_health_check_endpoint_sets_response_status():
    mock_db_success = MagicMock()
    response = Response()
    res_data = health_check(response=response, db=mock_db_success)
    assert response.status_code == status.HTTP_200_OK
    assert res_data.status == "healthy"

    mock_db_fail = MagicMock()
    mock_db_fail.execute.side_effect = Exception("DB down")
    response_fail = Response()
    res_data_fail = health_check(response=response_fail, db=mock_db_fail)
    assert response_fail.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert res_data_fail.status == "unhealthy"


def test_health_routes_registered_in_app():
    route_paths = [route.path for route in app.routes]
    
    # Root /health
    assert "/health" in route_paths
    # API v1 /api/v1/health
    assert "/api/v1/health" in route_paths
    # /heath alias redirect
    assert "/heath" in route_paths
