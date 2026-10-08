# app/tests/test_phase3_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_recommend_tables_endpoint_exists():
    res = client.get("/api/v1/tables/recommend?guests=4")
    assert res.status_code != 404

def test_reservation_checkin_endpoint_exists():
    res = client.post("/api/v1/reservations/999/checkin")
    assert res.status_code in (401, 404)
    if res.status_code == 404:
        assert "Reservation 999 not found" in str(res.json())
