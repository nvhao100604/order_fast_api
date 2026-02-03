import re
from sqlalchemy.orm import Session
from app.crud import dish as dish_crud
from app.models.catalog import Dish
from app.schemas.dish import DishCreate, DishUpdate

def get_all_dishes(db: Session, filters: dict, page: int = 1, limit: int = 10):
    """Xử lý logic phân trang và gọi CRUD"""
    if(page < 1 or limit < 1):
        raise ValueError("Page and limit must be positive integers.")
    skip = (page - 1) * limit
    if "categoryID" in filters and filters["categoryID"] < 0:
        dishes, total = dish_crud.get_all_dishes(db, skip=skip, limit=limit)
    else:
        dishes, total = dish_crud.get_dishes(db, filters=filters, skip=skip, limit=limit)

    return dishes, total

def get_dish(db: Session, dish_id: int):
    """Get a specific dish by ID"""
    if(dish_id < 1):
        raise ValueError("Dish ID must be a positive integer.")
    return dish_crud.get_dish(db, dish_id)

def get_dishes_by_name(db: Session, name: str, page: int = 1, limit: int = 10):
    """Lấy danh sách món ăn theo tên với phân trang"""
    if(page < 1 or limit < 1):
        raise ValueError("Page and limit must be positive integers.")
    skip = (page - 1) * limit
    if(not name):
        dishes = dish_crud.get_dishes(db, skip=skip, limit=limit)
        total = dish_crud.get_dish_count(db)
    else:
        dishes = dish_crud.get_dishes_by_name(db, name, skip=skip, limit=limit)
        total = dish_crud.get_dish_count_by_name(db, name)
    return dishes, total

def post_dish(db: Session, dish: DishCreate):
    """Thêm món ăn mới vào database"""
    new_dish = Dish(**dish.model_dump())
    return dish_crud.post_dish(db, new_dish)

def put_dish(db: Session, dish_id: int, updated_dish: DishCreate):
    """Cập nhật thông tin món ăn theo ID"""
    if(dish_id < 1):
        raise ValueError("Dish ID must be a positive integer.")
    updated_dish_model = Dish(**updated_dish.model_dump())
    return dish_crud.put_dish(db, dish_id, updated_dish_model)

def patch_dish(db: Session, dish_id: int, updated_fields: DishUpdate):
    """Cập nhật một số trường của món ăn theo ID"""
    blacklisted_keys = {"id", "created_at", "categoryID"} 

    if(dish_id < 1):
        raise ValueError("Dish ID must be a positive integer.")
    # Check and prepare update data
    update_data = updated_fields.model_dump(exclude_unset=True)
    if not update_data:
        raise ValueError("No valid fields provided for update.")
    # Check for blacklisted keys
    for key in update_data():
        if key in blacklisted_keys:
            raise ValueError(f"Trường '{key}' không được phép cập nhật thủ công.")
        
    return dish_crud.patch_dish(db, dish_id, update_data)

def delete_dish(db: Session, dish_id: int):
    """Xoá món ăn khỏi database theo ID"""
    if(dish_id < 1):
        raise ValueError("Dish ID must be a positive integer.")
    return dish_crud.delete_dish(db, dish_id)