from typing import List
from sqlalchemy.orm import Session
from app.crud import order as order_crud
from app.models.ordering import Order
from app.schemas.ordering import OrderCreate, OrderDetailBase

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
    order: OrderCreate,
    details: List[OrderDetailBase]
):
    order_in = Order(**order.model_dump())
    return order_crud.post_order(db=db, order=order_in, details_in=details)

def get_order(
    db: Session,
    id: int = 1
):
    if id < 1:
        raise ValueError("Order ID must be greater than 0.")
    return order_crud.get_order(db=db, id=id)