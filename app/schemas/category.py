from .base import BaseSchema

class CategoryBase(BaseSchema):
    name: str

class CategoryResponse(CategoryBase):
    id: int