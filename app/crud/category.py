from sqlalchemy.orm import Session
from app.models.catalog import Category

def get_categories(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Category)
    for key, value in filters.items():
        query = query.filter(getattr(Category, key) == value)
        
    total = query.count()
    categories = query.offset(skip).limit(limit).all()
    return categories, total