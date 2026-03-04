from datetime import datetime
from enum import IntEnum
from typing import Optional
from pydantic import Field
from app.models.enum import Status
from app.schemas.base import BaseSchema
from app.schemas.category import CategoryResponse

class DishStatus(IntEnum):
    OUT_OF_STOCK = 0
    IN_STOCK = 1
    DISCONTINUED = 2

class DishBase(BaseSchema):
    name: str
    price: float
    imgUrl: str
    describe: str
    status: str
    categoryID: int

class DishResponse(DishBase):
    id: int
    category: CategoryResponse
    createdAt: datetime
    updatedAt: datetime

class DishCreate(BaseSchema):
    name: str = Field(..., min_length=3, max_length=100, description="Dish name")
    price: float = Field(..., ge=0, description="Price must be non-negative")
    imgUrl: Optional[str] = Field(None, description="Dish image URL")
    describe: Optional[str] = Field(None, max_length=500, description="Dish description")
    categoryID: int = Field(..., ge=1, description="ID of category")

class DishUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    imgUrl: Optional[str] = None
    describe: Optional[str] = None
    categoryID: Optional[int] = None 
    status: Optional[str] = None

class DishFilter(BaseSchema):
    name: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    categoryID: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class DishDetail(BaseSchema):
    id: int
    name: str
    imgUrl: str