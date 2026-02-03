from sqlalchemy.orm import Session
from app.crud import category as category_crud

def get_categories(
    db: Session,
    filters: dict,
    page: int = 1,
    limit: int = 10,
):
    """Xử lý logic phân trang và gọi CRUD"""
    if(page < 1 or limit < 1):
        raise ValueError("Page must be a positive integer and limit must be a positive integer.")
    skip = (page - 1) * limit
    categories, total = category_crud.get_categories(db, filters=filters, skip=skip, limit=limit)

    return categories, total