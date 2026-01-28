from typing import Optional
from .base import BaseSchema

class CategoryBase(BaseSchema):
    name: str

class CategoryResponse(CategoryBase):
    id: int

class DishBase(BaseSchema):
    name: str
    price: float
    imgUrl: str
    describe: str
    status: int = 1
    categoryID: int

class DishResponse(DishBase):
    id: int