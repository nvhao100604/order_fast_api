from typing import List, Optional
from pydantic import Field, field_validator
from app.schemas.base import BaseSchema
from app.models.enum import FloorItemKind, TableShape
from app.schemas.ordering import TableResponse

class AreaBase(BaseSchema):
    name: str
    gridW: int = 30
    gridH: int = 20

class AreaResponse(AreaBase):
    id: int
    layoutVersion: int

class FloorItemBase(BaseSchema):
    tableId: Optional[int] = None
    kind: FloorItemKind
    shape: Optional[TableShape] = None
    x: int
    y: int
    w: int
    h: int
    rotation: int = 0

    @field_validator("w", "h")
    @classmethod
    def validate_positive_dimensions(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Dimensions w and h must be positive integers (> 0)")
        return v

class FloorItemCreate(FloorItemBase):
    pass

class FloorItemResponse(FloorItemBase):
    id: int
    areaId: int

class LayoutPayload(BaseSchema):
    layoutVersion: int
    items: List[FloorItemCreate]

class AreaLayoutResponse(AreaResponse):
    items: List[FloorItemResponse]
    tables: List[TableResponse]

class TableSuggestion(BaseSchema):
    tableIds: List[int]
    label: str  # FIT, EXTRA_CHAIR, OVERSIZED, MERGE
    spareSeats: int
