from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Dish

def get_dishes(db: Session, filters: dict, skip: int = 0, limit: int = 100):
    """Truy vấn danh sách món ăn từ DB có hỗ trợ phân trang"""
    query = db.query(Dish)

    if "name" in filters:
        query = query.filter(Dish.name.ilike(f"%{filters['name']}%"))
    
    if "categoryID" in filters:
        query = query.filter(Dish.categoryID == filters['categoryID'])
        
    if "status" in filters:
        query = query.filter(Dish.status == filters['status'])

    if "min_price" in filters:
        query = query.filter(Dish.price >= filters['min_price'])
    if "max_price" in filters:
        query = query.filter(Dish.price <= filters['max_price'])

    if "categoryID" in filters:
        query = query.filter(Dish.categoryID == filters['categoryID'])

    total = query.count()
    dishes = query.offset(skip).limit(limit).all()
    
    return dishes, total

def get_dish_count(db: Session) -> int:
    """Đếm tổng số món ăn trong database"""
    return db.query(func.count(Dish.id)).scalar()

def get_dish(db: Session, dish_id: int):
    """Truy vấn món ăn theo ID"""
    return db.query(Dish).filter(Dish.id == dish_id).first()

def post_dish(db: Session, dish: Dish):
    """Thêm món ăn mới vào database"""
    db.add(dish)
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

def put_dish(db: Session, dish_id: int, updated_dish: Dish):
    """Cập nhật thông tin món ăn theo ID"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if dish:
        dish.name = updated_dish.name
        dish.describe = updated_dish.describe
        dish.price = updated_dish.price
        db.commit()
        db.refresh(dish)
    return dish

def patch_dish(db: Session, dish_id: int, updated_fields: dict):
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

def get_dishes_by_name(db: Session, name: str, skip: int = 0, limit: int = 100):
    """Truy vấn danh sách món ăn theo tên từ DB có hỗ trợ phân trang"""
    query = db.query(Dish).filter(Dish.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()

def get_dish_count_by_name(db: Session, name: str) -> int:
    """Đếm tổng số món ăn theo tên trong database"""
    return db.query(func.count(Dish.id)).filter(Dish.name.ilike(f"%{name}%")).scalar()