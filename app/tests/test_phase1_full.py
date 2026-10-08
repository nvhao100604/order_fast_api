from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_user
from app.models.user import User

def test_phase1_full_flow():
    app.dependency_overrides[get_current_user] = lambda: User(id=1, username="testadmin", roleID=1)
    client = TestClient(app)

    # 1. Check Areas
    res = client.get("/api/v1/areas")
    assert res.status_code == 200
    areas = res.json()
    assert len(areas) >= 1
    area_id = areas[0]["id"]

    # 2. Check Area Layout
    res_layout = client.get(f"/api/v1/areas/{area_id}/layout")
    assert res_layout.status_code == 200
    layout_data = res_layout.json()
    assert "items" in layout_data
    assert "tables" in layout_data

    # 3. Test Layout Save with Conflict
    current_version = layout_data["layoutVersion"]
    bad_payload = {
        "layoutVersion": current_version + 99,
        "items": []
    }
    res_conflict = client.put(f"/api/v1/areas/{area_id}/layout", json=bad_payload)
    assert res_conflict.status_code == 409

    # 4. Check Unplaced tables endpoint
    res_unplaced = client.get("/api/v1/tables?unplaced=true")
    assert res_unplaced.status_code == 200



