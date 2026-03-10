from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enum import OrderStatus
from app.models.ordering import Order, Table

# def get_dashboard_guests_stats(db: Session):
#     today = date.today()
#     # Giả định User có trường createdAt
#     today_guests = db.query(User).filter(func.date(User.createdAt) == today).count()
#     today_reservations = db.query(Reservation).filter(func.date(Reservation.reservationDate) == today).count()
    
#     return today_guests, today_reservations

# def get_dashboard_orders_stats(db: Session):
#     today = date.today()
#     first_day_month = today.replace(day=1)

#     today_orders = db.query(Order).filter(func.date(Order.createdAt) == today).count()
#     # Giả định trạng thái 'pending' có trong Enum hoặc String
#     pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
#     monthly_orders = db.query(Order).filter(Order.createdAt >= first_day_month).count()

#     return today_orders, pending_orders, monthly_orders

def get_dashboard_revenue_stats(db: Session):
    today = date.today()
    first_day_month = today.replace(day=1)
    
    # Doanh thu hôm nay
    today_revenue = db.query(func.sum(Order.totalPrice)).filter(
        func.date(Order.createdAt) == today,
        Order.status == OrderStatus.COMPLETED
    ).scalar() or 0

    # Doanh thu tháng này
    monthly_revenue = db.query(func.sum(Order.totalPrice)).filter(
        Order.createdAt >= first_day_month,
        Order.status == OrderStatus.COMPLETED
    ).scalar() or 0

    return today_revenue, monthly_revenue

def get_all_orders(db: Session):
    return db.query(Order).all()

def get_all_tables(db: Session):
    return db.query(Table).all()