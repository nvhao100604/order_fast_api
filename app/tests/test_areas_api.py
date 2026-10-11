from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_areas_endpoint():
    response = client.get("/api/v1/areas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_unplaced_tables_endpoint():
    response = client.get("/api/v1/tables?unplaced=true")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

def test_put_area_layout_forbidden_for_customer():
    from app.api.deps import get_current_user
    from app.models.user import User
    from app.models.enum import Status
    from app.core.constants import RoleID

    customer_user = User(
        id=9999,
        username="customer_user",
        name="Customer",
        email="customer@example.com",
        roleID=RoleID.CUSTOMER,
        status=Status.ACTIVE
    )
    app.dependency_overrides[get_current_user] = lambda: customer_user
    try:
        response = client.put(
            "/api/v1/areas/1/layout",
            json={"layoutVersion": 1, "items": []}
        )
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


