from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import order as order_crud
from app.crud import dish as dish_crud
from app.crud import user as user_crud
from app.models.enum import OrderStatus
from app.models.ordering import Order
from app.models.user import User
from app.schemas.ordering import OrderCreate, OrderFilter

def get_orders(
    db: Session,
    filters: OrderFilter,        
    page: int = 1,
    limit: int = 10,
    current_user: User = None
):
    # 1. Validate user
    if current_user is None:
        raise ValueError("Current user is required.")

    user = user_crud.get_user_by_id(db=db, user_id=current_user.id)
    if not user:
        raise ValueError("User not found.")

    # 2. Validate pagination
    if page < 1:
        raise ValueError("Page must be a positive integer.")
    if not (1 <= limit <= 100):
        raise ValueError("Limit must be between 1 and 100.")

    # 3. Business logic: build filter theo role
    if user.roleID == 3:
        # Customer chỉ xem đơn của chính mình, bỏ qua staffID nếu có truyền
        filters_dict = filters.model_dump(exclude_none=True, exclude={"staffID"})
        filters_dict["customerID"] = current_user.id

    elif user.roleID == 2:
        # Staff có thể lọc theo staffID hoặc customerID tùy ý
        # Nếu không truyền staffID thì mặc định lấy đơn của chính staff đó
        filters_dict = filters.model_dump(exclude_none=True)
        if filters_dict.get("staffID") is None:
            filters_dict["staffID"] = current_user.id

    else:
        # Admin: xem tất cả, không ép filter
        filters_dict = filters.model_dump(exclude_none=True)

    # 4. Validate price range
    min_price = filters_dict.get("min_price")
    max_price = filters_dict.get("max_price")
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise ValueError("min_price must be less than or equal to max_price.")

    # 5. Query
    skip = (page - 1) * limit
    orders, total = order_crud.get_orders(
        db=db,
        filters=filters_dict,
        skip=skip,
        limit=limit,
    )
    return orders, total

def post_order(
    db: Session,
    order_in: OrderCreate
):
    if len(order_in.details) <= 0:
        raise ValueError("Order must contain at least one dish (details cannot be empty)!")
    p = order_in
    if (p.tax + p.subtotal + p.delivery) != p.totalPrice:
        raise ValueError("The sum of itemized costs does not match the total price provided.")
    
    # dump order data for crud
    order_data = order_in.model_dump()
    details_data = order_data.pop("details")

    cleaned_details = []
    for d in details_data:
        dish = dish_crud.get_dish(db=db, dish_id=d['dishID'])
        if not dish:
            raise HTTPException(status_code=404, detail=f"Dish ID {d['dishID']} does not exist.")
        
        # Chỉ lấy những trường mà Model OrderDetail cần (bỏ name, imgUrl...)
        cleaned_details.append({
            "dishID": d["dishID"],
            "quantity": d["quantity"],
            "price": d["price"]
        })

    order_in = Order(**order_data)
    return order_crud.post_order(db=db, order_in=order_in, details_in=cleaned_details)

def get_order(
    db: Session,
    id: int = 1
):
    if id < 1:
        raise ValueError("Order ID must be greater than 0.")
    return order_crud.get_order(db=db, id=id)

def update_order_status(
    db: Session,
    order_id: int,
    new_status: OrderStatus,
    current_staff: User
):
    """
    Cập nhật trạng thái đơn hàng.
    Kiểm tra ID đơn hàng trước khi thực hiện update.
    """

    if current_staff.id < 1:
        raise ValueError("Staff ID must be greater than 0.")
    
    if order_id < 1:
        raise ValueError("Order ID must be greater than 0.")

    staff = user_crud.get_user_by_id(db, current_staff.id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff with id {current_staff.id} not found."
        )

    order = order_crud.get_order(db=db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found."
        )
    
    return order_crud.update_order(
        db=db, 
        order_id=order_id, 
        updated_fields={
            "status": new_status,
            "staffID": current_staff.id
        }
    )