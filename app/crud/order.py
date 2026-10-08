from typing import List
from sqlalchemy import func, or_
from app.models.ordering import Order, OrderDetail
from sqlalchemy.orm import Session

from app.models.user import User

def get_orders(db: Session, filters: dict, skip: int = 0, limit: int = 10):
    query = db.query(Order)
    
    if filters.get("customer_search"):
        search_val = f"%{filters['customer_search']}%"
        query = query.join(Order.customer).filter(
            or_(
                func.unaccent(User.name).ilike(func.unaccent(search_val)),
                User.phoneNumber.ilike(search_val)
            )
        )

    if filters.get("staff_search"):
        search_val = f"%{filters['staff_search']}%"
        query = query.join(Order.staff).filter(
            or_(
                func.unaccent(User.name).ilike(func.unaccent(search_val)),
                User.phoneNumber.ilike(search_val)
            )
        )
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

from app.models.ordering import Order, OrderDetail, order_tables

def post_order(db: Session, order_in: Order, details_in: List[dict], table_ids: List[int] = None):
    db.add(order_in)
    db.flush()
    
    for detail in details_in:
        detail_db = OrderDetail(**detail, orderID=order_in.id)
        db.add(detail_db)

    # Phase 2: populate order_tables junction from table_ids and legacy tableID
    table_ids_to_link = list(table_ids or [])
    if order_in.tableID and order_in.tableID not in table_ids_to_link:
        table_ids_to_link.append(order_in.tableID)

    for tid in table_ids_to_link:
        try:
            db.execute(order_tables.insert().values(order_id=order_in.id, table_id=tid))
        except Exception:
            pass  # Ignore duplicate conflict

    db.commit()
    db.refresh(order_in)
    return order_in

def get_order(db: Session, id: int = 1):
    return db.query(Order).filter(Order.id == id).first()

def update_order(db: Session, order_id: int, updated_fields: dict):
    """Cập nhật các trường thông tin của đơn hàng (ví dụ: status)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        for key, value in updated_fields.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.commit()
        db.refresh(order)
    return order

def delete_order(db: Session, id: int):
    """Xóa đơn hàng (thường ít dùng, nên dùng Cancel thay thế)"""
    order = db.query(Order).filter(Order.id == id).first()
    if order:
        db.delete(order)
        db.commit()
        return True
    return False
