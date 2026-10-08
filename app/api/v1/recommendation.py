# app/api/v1/recommendation.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.ordering import TableResponse
from app.schemas.response import ResponseSchema
from app.services.table_recommendation import recommend_tables

router = APIRouter()


@router.get("/recommend", response_model=ResponseSchema[List[TableResponse]])
def recommend_tables_endpoint(
    guests: int = Query(..., ge=1, description="Number of guests requiring a table"),
    areaID: Optional[int] = Query(None, description="Optional area filter"),
    db: Session = Depends(get_db)
):
    tables = recommend_tables(db, guest_count=guests, area_id=areaID)
    return ResponseSchema[List[TableResponse]](
        data=tables,
        message=f"Found {len(tables)} recommended table(s) for {guests} guests."
    )
