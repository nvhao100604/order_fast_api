from typing import Optional
from .base import BaseSchema

class CategoryBase(BaseSchema):
    name: str

class CategoryResponse(CategoryBase):
    id: int

class CategoryFilter(BaseSchema):
    name: Optional[str] = None