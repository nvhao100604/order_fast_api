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

