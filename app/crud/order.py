from typing import List
from fastapi import HTTPException
from sqlalchemy import func
from app.models.catalog import Dish
from app.models.ordering import Order, OrderDetail
from sqlalchemy.orm import Session

from app.schemas.ordering import OrderDetailBase


def get_orders(db: Session, filters: dict, skip: int = 0, limit: int = 10):
    query = db.query(Order)
    if "staffID" in filters:
        query = query.filter(Order.staffID == filters["staffID"])

    if "customerID" in filters:
        query = query.filter(Order.customerID == filters["customerID"])

    if "tableID" in filters:
        query = query.filter(Order.tableID == filters["tableID"]) 

    if "dateOrder" in filters:
        query = query.filter(func.date(Order.dateOrder) == filters["dateOrder"])

    if "status" in filters:
        query = query.filter(Order.status == filters['status'])

    if "min_price" in filters and "max_price" in filters:
        min_price = filters['min_price']
        max_price = filters['max_price']
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValueError("The minimum price must be less than or equal the maximum price.")
            query = query.filter(Order.totalPrice >= min_price, Order.totalPrice <= max_price)
    
    total = query.count()
    orders = query.offset(skip).limit(limit).all()

    return orders, total

def post_order(db: Session, order_in: Order, details_in: List[OrderDetailBase]):
    db.add(order_in)
    db.flush()

    for detail in details_in:
        dish_exists = db.query(Dish).filter(Dish.id == detail.dishID).first()
    
        if not dish_exists:
            raise HTTPException(status_code=404, detail=f"Dish with ID {detail.dishID} is not exist!")
        detail_db = OrderDetail(**detail.model_dump(), orderID=order_in.id)
        db.add(detail_db)

    db.commit()
    db.refresh(order_in)
    return order_in

def get_order(db: Session, id: int = 1):
    order = db.query(Order).filter(Order.id == id).first()
    return order