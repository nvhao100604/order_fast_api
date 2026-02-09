from sqlalchemy.orm import Session
from app.crud import order as order_crud
from app.models.ordering import Order
from app.schemas.ordering import OrderCreate

def get_orders(
    db: Session,
    filters: dict,
    page: int = 1,
    limit: int = 10,
):
    if(page < 1 or limit < 1):
        raise ValueError("Page must be a positive integer and limit must be a positive integer.")
    skip = (page - 1) * limit
    orders, total = order_crud.get_orders(db=db, filters=filters, skip=skip, limit=limit)
    return orders, total

def post_order(
    db: Session,
    order: OrderCreate
):
    if len(order.details) <= 0:
        raise ValueError("Order must contain at least one dish (details cannot be empty)!")
    p = order.totalPrice
    if (p.tax + p.subtotal + p.delivery) != p.total:
        raise ValueError("The sum of itemized costs does not match the total price provided.")
    # dump order data for crud
    order_data = order.model_dump()
    details_data = order_data.pop("details")
    price_info = order_data.pop("totalPrice")
    order_data.update({
        "tax":price_info["tax"],
        "subtotal":price_info["subtotal"],
        "delivery":price_info["delivery"],
        "totalPrice": price_info["total"]
    })
    order_in = Order(**order_data)
    return order_crud.post_order(db=db, order_in=order_in, details_in=details_data)

def get_order(
    db: Session,
    id: int = 1
):
    if id < 1:
        raise ValueError("Order ID must be greater than 0.")
    return order_crud.get_order(db=db, id=id)