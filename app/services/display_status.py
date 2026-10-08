# app/services/display_status.py
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.ordering import Table, Order, order_tables
from app.models.reservation import Reservation
from app.models.enum import TableStatus, OrderStatus, ReservationStatus

_ACTIVE_ORDER_STATUSES = {
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED,
    OrderStatus.PREPARING,
    OrderStatus.SHIPPING,
    OrderStatus.UNPAID,
}
_RESERVATION_LOOKAHEAD_HOURS = 2


def compute_display_status(db: Session, table_id: int) -> str:
    """
    Compute the displayStatus for a single table (never persisted).

    Priority:
    1. table.status in (PAYING, CLEANING) -> use as-is
    2. active order linked via order_tables -> OCCUPIED
    3. upcoming confirmed reservation within 2h -> RESERVED
    4. fallback -> EMPTY
    """
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        return "EMPTY"

    # 1. Physical status overrides
    if table.status in (TableStatus.PAYING, TableStatus.CLEANING):
        return table.status.value

    # 2. Active order via order_tables
    active_count = (
        db.query(Order)
        .join(order_tables, Order.id == order_tables.c.order_id)
        .filter(
            order_tables.c.table_id == table_id,
            Order.status.in_(_ACTIVE_ORDER_STATUSES)
        )
        .count()
    )
    if active_count > 0:
        return "OCCUPIED"

    # 3. Upcoming confirmed reservation within lookahead window
    now = datetime.now(timezone.utc)
    lookahead = now + timedelta(hours=_RESERVATION_LOOKAHEAD_HOURS)
    upcoming = (
        db.query(Reservation)
        .filter(
            Reservation.tableID == table_id,
            Reservation.status == ReservationStatus.CONFIRMED,
            Reservation.reservationTime >= now,
            Reservation.reservationTime <= lookahead,
        )
        .count()
    )
    if upcoming > 0:
        return "RESERVED"

    return "EMPTY"


def batch_display_status(db: Session, table_ids: List[int]) -> Dict[int, str]:
    """Compute displayStatus for multiple tables. Returns {table_id: status}."""
    return {tid: compute_display_status(db, tid) for tid in table_ids}
