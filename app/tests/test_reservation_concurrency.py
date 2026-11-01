# app/tests/test_reservation_concurrency.py
from datetime import datetime, timezone, timedelta
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.enum import TableStatus, ReservationStatus
from app.models.ordering import Table
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate
from app.services.reservation import create_reservation_service


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_concurrent_reservation_overlap_raises_409(db):
    table = Table(number=101, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    db.add(table)
    db.commit()

    slot = datetime(2030, 5, 1, 18, 0, tzinfo=timezone.utc)
    res_in_1 = ReservationCreate(
        fullName="User A", email="a@example.com", phoneNumber="0901111111",
        numberOfGuests=2, reservationTime=slot, tableID=table.id
    )
    create_reservation_service(db=db, data=res_in_1)

    # User B tries to book the same table 30 mins later (within default 90m + 15m hold)
    res_in_2 = ReservationCreate(
        fullName="User B", email="b@example.com", phoneNumber="0902222222",
        numberOfGuests=2, reservationTime=slot + timedelta(minutes=30), tableID=table.id
    )

    with pytest.raises(HTTPException) as exc:
        create_reservation_service(db=db, data=res_in_2)
    assert exc.value.status_code == 409
    assert "đã có khách đặt" in exc.value.detail or "already reserved" in exc.value.detail.lower()
