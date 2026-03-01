from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Dish

def get_all_dishes(db: Session, skip: int = 0, limit: int = 10):
    """Truy vấn tất cả món ăn từ DB"""
    dishes = db.query(Dish).offset(skip).limit(limit).all()
    total = db.query(func.count(Dish.id)).scalar()
    return dishes, total

def get_dishes(db: Session, filters: dict, skip: int = 0, limit: int = 10):
    """Truy vấn danh sách món ăn từ DB có hỗ trợ phân trang"""
    query = db.query(Dish)

    if "categoryID" in filters:
        category_id = filters.get("categoryID")
        # print("check id: ", category_id)
        if category_id > 0:
            query = query.filter(Dish.categoryID == filters['categoryID'])

    if "name" in filters:
        query = query.filter(
            func.unaccent(Dish.name).ilike(func.unaccent(f"%{filters['name']}%")))
        
    if "status" in filters:
        query = query.filter(Dish.status == filters['status'])

    if "min_price" in filters and "max_price" in filters:
        query = query.filter(Dish.price >= filters['min_price'])

    if "max_price" in filters:
        query = query.filter(Dish.price <= filters['max_price'])

    if filters.get("start_date"):
        query = query.filter(Dish.createdAt >= filters["start_date"])

    if filters.get("end_date"):
        query = query.filter(Dish.createdAt <= filters["end_date"])

    query = query.order_by(Dish.createdAt.desc())

    total = query.count()
    dishes = query.offset(skip).limit(limit).all()
    
    return dishes, total

def get_dish(db: Session, dish_id: int):
    """Truy vấn món ăn theo ID"""
    return db.query(Dish).filter(Dish.id == dish_id).first()

def post_dish(db: Session, dish: Dish):
    """Thêm món ăn mới vào database"""
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish

def update_dish(db: Session, dish_id: int, updated_fields: dict):
    """Cập nhật một số trường của món ăn theo ID"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if dish:
        for key, value in updated_fields.items():
            setattr(dish, key, value)
        db.commit()
        db.refresh(dish)
    return dish

def delete_dish(db: Session, dish_id: int):
    """Xoá món ăn khỏi database theo ID"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if dish:
        db.delete(dish)
        db.commit()
    return dish