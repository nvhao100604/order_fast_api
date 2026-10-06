from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import category as category_crud
from app.models.catalog import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

def get_categories(
    db: Session,
    filters: dict,
    page: int = 1,
    limit: int = 10,
):
    """Xử lý logic phân trang và gọi CRUD"""
    if page < 1 or limit < 1:
        raise ValueError("Page must be a positive integer and limit must be a positive integer.")
    skip = (page - 1) * limit
    categories, total = category_crud.get_categories(db, filters=filters, skip=skip, limit=limit)
    return categories, total

def create_category_service(db: Session, data: CategoryCreate) -> Category:
    category = Category(name=data.name)
    return category_crud.create_category(db, category)

def update_category_service(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found."
        )
    fields_dict = data.model_dump(exclude_none=True)
    return category_crud.update_category(db, category_id, fields_dict)

def delete_category_service(db: Session, category_id: int) -> Category:
    category = category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found."
        )
    return category_crud.delete_category(db, category_id)