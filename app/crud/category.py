from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from app.models.catalog import Category

def get_categories(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[Category], int]:
    query = db.query(Category)
    for key, value in filters.items():
        if hasattr(Category, key):
            query = query.filter(getattr(Category, key) == value)
        
    total = query.count()
    categories = query.offset(skip).limit(limit).all()
    return categories, total

def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()

def create_category(db: Session, category: Category) -> Category:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def update_category(db: Session, category_id: int, updated_fields: dict) -> Optional[Category]:
    category = get_category_by_id(db, category_id)
    if category:
        for key, value in updated_fields.items():
            if hasattr(category, key):
                setattr(category, key, value)
        db.commit()
        db.refresh(category)
    return category

def delete_category(db: Session, category_id: int) -> Optional[Category]:
    category = get_category_by_id(db, category_id)
    if category:
        db.delete(category)
        db.commit()
    return category