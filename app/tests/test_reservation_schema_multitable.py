# app/tests/test_reservation_schema_multitable.py
import pytest
from datetime import datetime, timezone
from app.schemas.reservation import ReservationCreate, ReservationResponse

def test_reservation_create_accepts_table_ids():
    res = ReservationCreate(
        fullName="John Doe",
        email="john@example.com",
        phoneNumber="0912345678",
        numberOfGuests=4,
        reservationTime=datetime.now(timezone.utc),
        tableIDs=[1, 2],
    )
    assert res.tableIDs == [1, 2]

def test_reservation_create_table_ids_defaults_empty():
    res = ReservationCreate(
        fullName="Jane Doe",
        email="jane@example.com",
        phoneNumber="0987654321",
        numberOfGuests=2,
        reservationTime=datetime.now(timezone.utc),
    )
    assert res.tableIDs == []
