from typing import Tuple, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.reservation import Reservation

def get_reservations(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[Reservation], int]:
    """Truy vấn danh sách đặt bàn có phân trang và bộ lọc"""
    query = db.query(Reservation)

    if filters.get("status"):
        query = query.filter(Reservation.status == filters["status"])

    if filters.get("email"):
        query = query.filter(Reservation.email.ilike(f"%{filters['email']}%"))

    if filters.get("phoneNumber"):
        query = query.filter(Reservation.phoneNumber.ilike(f"%{filters['phoneNumber']}%"))

    if filters.get("userID"):
        query = query.filter(Reservation.userID == filters["userID"])

    if filters.get("tableID"):
        query = query.filter(Reservation.tableID == filters["tableID"])

    if filters.get("startDate"):
        query = query.filter(Reservation.reservationTime >= filters["startDate"])

    if filters.get("endDate"):
        query = query.filter(Reservation.reservationTime <= filters["endDate"])

    query = query.order_by(Reservation.reservationTime.desc())
    total = query.count()
    reservations = query.offset(skip).limit(limit).all()

    return reservations, total

def get_reservation_by_id(db: Session, reservation_id: int) -> Optional[Reservation]:
    """Lấy thông tin chi tiết đặt bàn theo ID"""
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()

def create_reservation(db: Session, reservation: Reservation) -> Reservation:
    """Tạo lượt đặt bàn mới"""
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation

def update_reservation(db: Session, reservation_id: int, updated_fields: dict) -> Optional[Reservation]:
    """Cập nhật các trường thông tin của lượt đặt bàn"""
    reservation = get_reservation_by_id(db, reservation_id)
    if reservation:
        for key, value in updated_fields.items():
            if hasattr(reservation, key):
                setattr(reservation, key, value)
        db.commit()
        db.refresh(reservation)
    return reservation

def delete_reservation(db: Session, reservation_id: int) -> Optional[Reservation]:
    """Xóa bản ghi đặt bàn"""
    reservation = get_reservation_by_id(db, reservation_id)
    if reservation:
        db.delete(reservation)
        db.commit()
    return reservation
