from sqlalchemy.orm import Session
from app.crud import dish as dish_crud
from app.models.catalog import Dish
from app.schemas.dish import DishCreate, DishUpdate

def get_all_dishes(db: Session, filters: dict, page: int = 1, limit: int = 10):
    """Xử lý logic phân trang và gọi CRUD"""
    if(page < 1 or limit < 1):
        raise ValueError("Page must be a positive integer and limit must be a positive integer.")
    if "min_price" in filters and "max_price" in filters:
        min_price = filters['min_price']
        max_price = filters['max_price']
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValueError("The minimum price must be less than or equal the maximum price.")
    skip = (page - 1) * limit
    dishes, total = dish_crud.get_dishes(db, filters=filters, skip=skip, limit=limit)

    return dishes, total

def get_dish(db: Session, dish_id: int):
    """Get a specific dish by ID"""
    if(dish_id < 1):
        raise ValueError("Dish ID must be a positive integer.")
    return dish_crud.get_dish(db, dish_id)

def post_dish(db: Session, dish: DishCreate):
    """Thêm món ăn mới vào database"""
    new_dish = Dish(**dish.model_dump())
    return dish_crud.post_dish(db, new_dish)

def put_dish(db: Session, dish_id: int, updated_dish: DishCreate):
    """Cập nhật thông tin món ăn theo ID"""
    if(dish_id < 1):
        raise ValueError("Dish ID must be a positive integer.")
    
    updated_dish_model = Dish(**updated_dish.model_dump())
    return dish_crud.update_dish(db, dish_id, updated_dish_model)

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
            raise ValueError(f"Field '{key}' is read-only and cannot be modified.")   
    return dish_crud.update_dish(db, dish_id, update_data)

def delete_dish(db: Session, dish_id: int):
    """Xoá món ăn khỏi database theo ID"""
    if(dish_id < 1):
        raise ValueError("Dish ID must be a positive integer.")
    return dish_crud.delete_dish(db, dish_id)