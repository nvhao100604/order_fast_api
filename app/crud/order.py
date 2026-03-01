from typing import List
from sqlalchemy import func
from app.models.ordering import Order, OrderDetail
from sqlalchemy.orm import Session

def get_orders(db: Session, filters: dict, skip: int = 0, limit: int = 10):
    query = db.query(Order)
    
    if "staffID" in filters:
        query = query.filter(Order.staffID == filters["staffID"])

    if "customerID" in filters:
        query = query.filter(Order.customerID == filters["customerID"])

    if "tableID" in filters:
        query = query.filter(Order.tableID == filters["tableID"]) 

    if "dateOrder" in filters:
        query = query.filter(func.date(Order.createdAt) == filters["dateOrder"])

    if "status" in filters:
        query = query.filter(Order.status == filters['status'])

    if "min_price" in filters:
        query = query.filter(Order.totalPrice >= filters["min_price"])
    
    if "max_price" in filters:
        query = query.filter(Order.totalPrice <= filters["max_price"])

    if filters.get("start_date"):
        query = query.filter(Order.createdAt >= filters["start_date"])

    if filters.get("end_date"):
        query = query.filter(Order.createdAt <= filters["end_date"])
    
    
    query = query.order_by(Order.createdAt.desc())
    
    total = query.count()
    orders = query.offset(skip).limit(limit).all()

    return orders, total

def post_order(db: Session, order_in: Order, details_in: List[dict]):
    db.add(order_in)
    db.flush()
    
    for detail in details_in:
        detail_db = OrderDetail(**detail, orderID=order_in.id)
        db.add(detail_db)

    db.commit()
    db.refresh(order_in)
    return order_in

def get_order(db: Session, id: int = 1):
    return db.query(Order).filter(Order.id == id).first()
