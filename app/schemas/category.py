from datetime import datetime
from typing import Optional
from .base import BaseSchema

class CategoryBase(BaseSchema):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseSchema):
    name: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    status: str = "active"
    createdAt: datetime
    updatedAt: datetime

class CategoryFilter(BaseSchema):
    name: Optional[str] = None