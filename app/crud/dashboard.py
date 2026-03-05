# from datetime import datetime, date

# from sqlalchemy import func
# from sqlalchemy.orm import Session
# from app.models import User, Reservation, Order, Table, OrderDetail, Dish
# from app.models.enum import OrderStatus, TableStatus

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

# def get_dashboard_revenue_stats(db: Session):
#     today = date.today()
#     first_day_month = today.replace(day=1)
    
#     # Doanh thu hôm nay
#     today_revenue = db.query(func.sum(Order.totalPrice)).filter(
#         func.date(Order.createdAt) == today,
#         Order.status == "paid" # Chỉ tính đơn đã thanh toán
#     ).scalar() or 0

#     # Doanh thu tháng này
#     monthly_revenue = db.query(func.sum(Order.totalPrice)).filter(
#         Order.createdAt >= first_day_month,
#         Order.status == "paid"
#     ).scalar() or 0

#     # Tăng trưởng (Ví dụ đơn giản: So sánh doanh thu hôm nay với trung bình ngày tháng trước hoặc hôm qua)
#     # Ở đây tôi giả định bạn trả về một con số % dựa trên logic nghiệp vụ của bạn
#     revenue_growth = 15.5 # Ví dụ fix cứng hoặc tính toán thêm

#     return today_revenue, monthly_revenue, revenue_growth

# def get_dashboard_tables_stats(db: Session):
#     available = db.query(Table).filter(Table.status == TableStatus.EMPTY).count()
#     occupied = db.query(Table).filter(Table.status == TableStatus.OCCUPIED).count()
#     RESERVEd = db.query(Table).filter(Table.status == TableStatus.RESERVED).count()

#     return available, occupied, RESERVEd