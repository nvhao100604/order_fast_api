from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import order as order_crud
from app.crud import dish as dish_crud
from app.crud import user as user_crud
from app.models.enum import OrderStatus
from app.models.ordering import Order
from app.schemas.ordering import OrderCreate

def get_orders(
    db: Session,
    filters: dict,
    page: int = 1,
    limit: int = 10,
    current_user: int = None
):
    if current_user is None:
        raise ValueError("Current user is required.")
    if(page < 1 or limit < 1):
        raise ValueError("Page must be a positive integer and limit must be a positive integer.")
    if "min_price" in filters and "max_price" in filters:
        min_price = filters['min_price']
        max_price = filters['max_price']
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValueError("The minimum price must be less than or equal the maximum price.")
    user = user_crud.get_user_by_id(db=db, user_id=current_user)
    if not user:
        raise ValueError("User not found.")
    
    skip = (page - 1) * limit
    orders, total = order_crud.get_orders(db=db, filters=filters, skip=skip, limit=limit, current_user=current_user)
    return orders, total

def post_order(
    db: Session,
    order: OrderCreate
):
    if len(order.details) <= 0:
        raise ValueError("Order must contain at least one dish (details cannot be empty)!")
    p = order
    if (p.tax + p.subtotal + p.delivery) != p.totalPrice:
        raise ValueError("The sum of itemized costs does not match the total price provided.")
    # dump order data for crud
    order_data = order.model_dump()
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

    price_info = order_data.pop("totalPrice")
    order_data.update({
        "tax":price_info["tax"],
        "subtotal":price_info["subtotal"],
        "delivery":price_info["delivery"],
        "totalPrice": price_info["total"]
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
    new_status: OrderStatus
):
    """
    Cập nhật trạng thái đơn hàng.
    Kiểm tra ID đơn hàng trước khi thực hiện update.
    """
    if order_id < 1:
        raise ValueError("Order ID must be greater than 0.")

    order = order_crud.get_order(db=db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found."
        )
    
    return order_crud.update_order(
        db=db, 
        order_id=order_id, 
        updated_fields={"status": new_status}
    )