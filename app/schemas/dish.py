from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema

class DishBase(BaseSchema):
    name: str
    price: float
    imgUrl: str
    describe: str
    status: int = 1
    categoryID: int

class DishResponse(DishBase):
    id: int

class DishDetail(BaseSchema):
    id: int
    name: str
    imgUrl: str


class DishCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Dish name")
    price: float = Field(..., ge=0, description="price must be non-negative")
    imgUrl: Optional[str] = Field(..., description="Dish image URL")
    describe: Optional[str] = Field(None, max_length=500, description="Dish description")
    categoryID: int = Field(..., ge=1, description="ID of category the dish belongs to")
    status: int = Field(1, ge=0, le=2, description="0: out stock, 1: in stock, 2: discontinued")

class DishUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    imgUrl: Optional[str] = None
    describe: Optional[str] = None
    categoryID: Optional[int] = None
    status: Optional[int] = None
    categoryID: Optional[int] = None

class DishFilter(BaseModel):
    name: Optional[str] = Field(None, description="Filter by dish name")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    categoryID: Optional[int] = Field(None, description="Filter by category ID")
    status: Optional[int] = Field(None, description="Filter by dish status")