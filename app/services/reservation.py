from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.constants import RoleID
from app.crud import reservation as reservation_crud
from app.crud import table as table_crud
from app.models.enum import ReservationStatus, TableStatus
from app.models.ordering import Table
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationUpdate

def _lock_tables_for_update(db: Session, table_ids: List[int]) -> List[Table]:
    """Khóa các hàng Table theo thứ tự id tăng dần để tránh Deadlock."""
    if not table_ids:
        return []
    sorted_ids = sorted(list(set(table_ids)))
    try:
        stmt = select(Table).filter(Table.id.in_(sorted_ids)).order_by(Table.id.asc()).with_for_update()
        tables = db.execute(stmt).scalars().all()
    except Exception:
        # SQLite graceful fallback for test environment
        tables = db.query(Table).filter(Table.id.in_(sorted_ids)).order_by(Table.id.asc()).all()
    return tables

def create_reservation_service(
    db: Session,
    data: ReservationCreate,
    current_user: Optional[User] = None
) -> Reservation:
    """Tạo đơn đặt bàn mới với cơ chế khóa dòng và kiểm tra xung đột thời gian"""
    # 1. Kiểm tra thời gian đặt bàn phải ở tương lai
    now = datetime.now(timezone.utc)
    res_time = data.reservationTime
    if res_time.tzinfo is None:
        res_time = res_time.replace(tzinfo=timezone.utc)

    if res_time <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation time must be in the future."
        )

    # 2. Xử lý userID
    user_id = data.userID
    if current_user:
        if current_user.roleID == RoleID.CUSTOMER:
            user_id = current_user.id
        elif not user_id:
            user_id = current_user.id

    table_ids = list(getattr(data, "tableIDs", []) or [])
    if data.tableID and data.tableID not in table_ids:
        table_ids.append(data.tableID)

    primary_table_id = data.tableID or (table_ids[0] if table_ids else None)

    # 3. Khóa bàn và kiểm tra xung đột khung giờ (Pessimistic Locking & Overlap Validation)
    if table_ids:
        locked_tables = _lock_tables_for_update(db, table_ids)
        if len(locked_tables) != len(table_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more selected tables not found."
            )

        for t in locked_tables:
            if t.status == TableStatus.DELETED or getattr(t, "walkInOnly", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bàn số {t.number} không khả dụng để đặt trước."
                )

        duration = getattr(data, "durationMinutes", None) or 90
        turnover = 15
        new_start = res_time
        new_end = new_start + timedelta(minutes=duration + turnover)

        active_res = (
            db.query(Reservation)
            .filter(
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED]),
                or_(
                    Reservation.tableID.in_(table_ids),
                    Reservation.tables.any(Table.id.in_(table_ids))
                )
            )
            .all()
        )

        for r in active_res:
            r_start = r.reservationTime.replace(tzinfo=timezone.utc) if r.reservationTime.tzinfo is None else r.reservationTime
            r_dur = getattr(r, "durationMinutes", None) or 90
            r_end = r_start + timedelta(minutes=r_dur + 15)
            if r_start < new_end and new_start < r_end:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Bàn đã có khách đặt trong khung giờ này. Vui lòng chọn bàn hoặc thời gian khác."
                )

    reservation = Reservation(
        fullName=data.fullName,
        email=data.email,
        phoneNumber=data.phoneNumber,
        numberOfGuests=data.numberOfGuests,
        reservationTime=data.reservationTime,
        specialRequests=data.specialRequests,
        status=ReservationStatus.PENDING,
        userID=user_id,
        tableID=primary_table_id
    )

    return reservation_crud.create_reservation(db=db, reservation=reservation, table_ids=table_ids)

def get_reservations_service(
    db: Session,
    filters: dict,
    page: int = 1,
    limit: int = 10,
    current_user: Optional[User] = None
) -> Tuple[List[Reservation], int]:
    """Lấy danh sách đặt bàn có phân trang và bộ lọc"""
    skip = (page - 1) * limit

    # Khách hàng thông thường chỉ xem được danh sách đặt bàn của chính họ
    if current_user and current_user.roleID == RoleID.CUSTOMER:
        filters["userID"] = current_user.id

    return reservation_crud.get_reservations(db=db, filters=filters, skip=skip, limit=limit)

def get_reservation_detail_service(
    db: Session,
    reservation_id: int,
    current_user: Optional[User] = None
) -> Reservation:
    """Lấy thông tin chi tiết một lượt đặt bàn"""
    reservation = reservation_crud.get_reservation_by_id(db=db, reservation_id=reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found."
        )

    # Kiểm tra phân quyền truy cập
    if current_user and current_user.roleID == RoleID.CUSTOMER:
        if reservation.userID != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Do not have permission to view this reservation."
            )

    return reservation

def update_reservation_service(
    db: Session,
    reservation_id: int,
    update_data: ReservationUpdate,
    current_user: Optional[User] = None
) -> Reservation:
    """Cập nhật thông tin / trạng thái / gán bàn cho lịch đặt bàn"""
    reservation = reservation_crud.get_reservation_by_id(db=db, reservation_id=reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found."
        )

    # Kiểm tra quyền nếu là Khách hàng (chỉ cho phép cập nhật thông tin khi trạng thái PENDING)
    if current_user and current_user.roleID == RoleID.CUSTOMER:
        if reservation.userID != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Do not have permission to modify this reservation."
            )
        if reservation.status != ReservationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify reservation after it has been processed."
            )

    fields_to_update = update_data.model_dump(exclude_unset=True)

    # Nếu có gán tableID, kiểm tra sự tồn tại của bàn ăn
    if "tableID" in fields_to_update and fields_to_update["tableID"] is not None:
        table_obj = table_crud.get_table(db=db, table_id=fields_to_update["tableID"])
        if not table_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table with ID {fields_to_update['tableID']} not found."
            )
        # Khi gán bàn và trạng thái được xác nhận (CONFIRMED), đổi trạng thái bàn sang RESERVED
        new_status = fields_to_update.get("status", reservation.status)
        if new_status == ReservationStatus.CONFIRMED:
            table_crud.update_table(db=db, table_id=table_obj.id, updated_fields={"status": TableStatus.RESERVED})

    updated_reservation = reservation_crud.update_reservation(
        db=db,
        reservation_id=reservation_id,
        updated_fields=fields_to_update
    )
    return updated_reservation

def cancel_reservation_service(
    db: Session,
    reservation_id: int,
    current_user: Optional[User] = None
) -> Reservation:
    """Hủy lượt đặt bàn"""
    reservation = reservation_crud.get_reservation_by_id(db=db, reservation_id=reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found."
        )

    if current_user and current_user.roleID == RoleID.CUSTOMER:
        if reservation.userID != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Do not have permission to cancel this reservation."
            )

    if reservation.status in [ReservationStatus.COMPLETED, ReservationStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a reservation that is already {reservation.status.value}."
        )

    # Nếu đã được gán bàn, giải phóng bàn ăn về EMPTY
    if reservation.tableID:
        table_crud.update_table(db=db, table_id=reservation.tableID, updated_fields={"status": TableStatus.EMPTY})

    return reservation_crud.update_reservation(
        db=db,
        reservation_id=reservation_id,
        updated_fields={"status": ReservationStatus.CANCELLED}
    )

def delete_reservation_service(db: Session, reservation_id: int) -> Reservation:
    """Xóa lịch đặt bàn (dành cho Admin)"""
    reservation = reservation_crud.get_reservation_by_id(db=db, reservation_id=reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found."
        )
    return reservation_crud.delete_reservation(db=db, reservation_id=reservation_id)
