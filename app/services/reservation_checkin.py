# app/services/reservation_checkin.py
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.reservation import Reservation, reservation_tables
from app.models.ordering import Table, Order, order_tables
from app.models.enum import ReservationStatus, TableStatus, OrderStatus


def checkin_reservation(
    db: Session,
    reservation_id: int,
    staff_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Check-in a confirmed reservation:
    1. Validates reservation exists & status is CONFIRMED or PENDING.
    2. Marks reservation as COMPLETED.
    3. Opens all linked tables (sets status to OCCUPIED).
    4. Automatically creates an active draft Order linked to all tables via order_tables.
    """
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found"
        )

    if res.status not in (ReservationStatus.CONFIRMED, ReservationStatus.PENDING):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Reservation {reservation_id} with status '{res.status.value}' cannot be checked in"
        )

    # Collect all associated tables (M2M tables or legacy tableID)
    linked_tables = list(res.tables or [])
    if res.tableID and not any(t.id == res.tableID for t in linked_tables):
        legacy_t = db.query(Table).filter(Table.id == res.tableID).first()
        if legacy_t:
            linked_tables.append(legacy_t)

    # Update reservation status
    res.status = ReservationStatus.COMPLETED

    # Update linked tables status to OCCUPIED
    for table in linked_tables:
        table.status = TableStatus.OCCUPIED

    # Create draft order if tables exist
    new_order = None
    if linked_tables:
        new_order = Order(
            status=OrderStatus.PENDING,
            totalPrice=0.0,
            subtotal=0.0,
            tax=0.0,
            delivery=0.0,
            staffID=staff_id,
            customerID=res.userID or staff_id,
            tableID=linked_tables[0].id  # legacy primary table
        )
        db.add(new_order)
        db.flush()

        # Link all tables in order_tables
        for table in linked_tables:
            try:
                db.execute(order_tables.insert().values(order_id=new_order.id, table_id=table.id))
            except Exception:
                pass

    db.commit()
    db.refresh(res)
    if new_order:
        db.refresh(new_order)

    return {
        "reservation": res,
        "order": new_order,
        "tables": linked_tables
    }
