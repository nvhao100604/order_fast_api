import pytest
from fastapi import HTTPException
from app.db.session import SessionLocal
from app.services import layout as layout_service
from app.schemas.layout import LayoutPayload, FloorItemCreate

def test_get_all_areas():
    db = SessionLocal()
    try:
        areas = layout_service.get_all_areas(db)
        assert len(areas) >= 1
        assert areas[0].name == "Tầng 1"
    finally:
        db.close()

def test_save_layout_optimistic_locking_conflict():
    db = SessionLocal()
    try:
        areas = layout_service.get_all_areas(db)
        area_id = areas[0].id
        payload = LayoutPayload(
            layoutVersion=999,  # Wrong version
            items=[]
        )
        with pytest.raises(HTTPException) as exc_info:
            layout_service.save_area_layout(db, area_id, payload)
        assert exc_info.value.status_code == 409
    finally:
        db.close()
