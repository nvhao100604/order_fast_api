from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services import layout as layout_service
from app.schemas.layout import AreaResponse, AreaLayoutResponse, LayoutPayload

public_router = APIRouter()
private_router = APIRouter()

@public_router.get("", response_model=List[AreaResponse])
def read_areas(db: Session = Depends(get_db)):
    return layout_service.get_all_areas(db)

@public_router.get("/{area_id}/layout", response_model=AreaLayoutResponse)
def read_area_layout(area_id: int, db: Session = Depends(get_db)):
    area, items, tables = layout_service.get_area_layout(db, area_id)
    return {
        "id": area.id,
        "name": area.name,
        "gridW": area.gridW,
        "gridH": area.gridH,
        "layoutVersion": area.layoutVersion,
        "items": items,
        "tables": tables
    }

@private_router.put("/{area_id}/layout", response_model=AreaLayoutResponse)
@public_router.put("/{area_id}/layout", response_model=AreaLayoutResponse)
def update_area_layout(area_id: int, payload: LayoutPayload, db: Session = Depends(get_db)):
    area, items, tables = layout_service.save_area_layout(db, area_id, payload)
    return {
        "id": area.id,
        "name": area.name,
        "gridW": area.gridW,
        "gridH": area.gridH,
        "layoutVersion": area.layoutVersion,
        "items": items,
        "tables": tables
    }
