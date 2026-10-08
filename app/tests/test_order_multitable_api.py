# app/tests/test_order_multitable_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_open_table_endpoint_not_404():
    response = client.post("/api/v1/tables/1/open")
    assert response.status_code != 404

def test_merge_tables_endpoint_not_404():
    response = client.post("/api/v1/tables/merge", json={"tableIDs": [1, 2]})
    assert response.status_code != 404

def test_split_table_endpoint_not_404():
    response = client.post("/api/v1/tables/1/split")
    assert response.status_code != 404

def test_close_table_endpoint_not_404():
    response = client.post("/api/v1/tables/1/close")
    assert response.status_code != 404
