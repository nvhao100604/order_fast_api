# app/tests/test_phase3_full.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.ordering import Table
from app.models.reservation import Reservation, reservation_tables
from app.models.user import User, Role
from app.models.enum import TableStatus, ReservationStatus
from app.services import table_recommendation, reservation_checkin

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
    staff = User(username="staff_p3", email="p3@x.com", password="x", name="P3 Staff", phoneNumber="0900000099", roleID=role.id)
    session.add(staff)
    session.flush()
    session.staff_id = staff.id
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_full_phase3_flow(db):
    # 1. Create 2 small tables
    t1 = Table(number=101, minCapacity=2, seats=2, maxCapacity=2, status=TableStatus.EMPTY)
    t2 = Table(number=102, minCapacity=2, seats=2, maxCapacity=2, status=TableStatus.EMPTY)
    db.add_all([t1, t2])
    db.commit()

    # 2. Recommend tables for 4 guests -> returns [t1, t2] combo
    recs = table_recommendation.recommend_tables(db, guest_count=4)
    assert len(recs) == 2

    # 3. Create multi-table reservation for 4 guests with recommended tables
    res = Reservation(
        fullName="Multi Table Guest", email="mt@x.com", phoneNumber="0911223344",
        numberOfGuests=4, reservationTime=datetime.now(timezone.utc),
        status=ReservationStatus.CONFIRMED, tableID=t1.id
    )
    db.add(res)
    db.flush()
    for t in recs:
        db.execute(reservation_tables.insert().values(reservation_id=res.id, table_id=t.id))
    db.commit()

    # 4. Checkin reservation -> completes reservation, opens both tables, creates order
    checkin_res = reservation_checkin.checkin_reservation(db, res.id, staff_id=db.staff_id)
    assert checkin_res["reservation"].status == ReservationStatus.COMPLETED
    assert checkin_res["order"] is not None
    assert len(checkin_res["tables"]) == 2
    assert all(t.status == TableStatus.OCCUPIED for t in checkin_res["tables"])
