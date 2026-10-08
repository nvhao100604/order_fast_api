from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import layout as layout_service
from app.schemas.layout import AreaResponse, AreaLayoutResponse, LayoutPayload

router = APIRouter()

@router.get("", response_model=List[AreaResponse])
def read_areas(db: Session = Depends(get_db)):
    return layout_service.get_all_areas(db)

@router.get("/{area_id}/layout", response_model=AreaLayoutResponse)
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

@router.put("/{area_id}/layout", response_model=AreaLayoutResponse)
def update_area_layout(
    area_id: int, 
    payload: LayoutPayload, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
