# app/tests/test_reservation_checkin.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.ordering import Table, Order
from app.models.reservation import Reservation, reservation_tables
from app.models.user import User, Role
from app.models.enum import TableStatus, ReservationStatus, OrderStatus
from app.services import reservation_checkin

SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    role = Role(name="Staff")
    session.add(role)
    session.flush()
    staff = User(username="staff1", email="s1@x.com", password="x", name="S1", phoneNumber="0900000001", roleID=role.id)
    session.add(staff)
    session.flush()
    session.staff_id = staff.id
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_checkin_reservation_opens_tables_and_creates_order(db):
    t1 = Table(number=1, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    t2 = Table(number=2, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    db.add_all([t1, t2])
    db.commit()

    res = Reservation(
        fullName="Jane Doe", email="jane@x.com", phoneNumber="0987654321",
        numberOfGuests=4, reservationTime=datetime.now(timezone.utc),
        status=ReservationStatus.CONFIRMED, tableID=t1.id
    )
    db.add(res)
    db.flush()
    db.execute(reservation_tables.insert().values(reservation_id=res.id, table_id=t1.id))
    db.execute(reservation_tables.insert().values(reservation_id=res.id, table_id=t2.id))
    db.commit()

    result = reservation_checkin.checkin_reservation(db, res.id, staff_id=db.staff_id)
    assert result["reservation"].status == ReservationStatus.COMPLETED
    assert t1.status == TableStatus.OCCUPIED
    assert t2.status == TableStatus.OCCUPIED
    assert result["order"] is not None
