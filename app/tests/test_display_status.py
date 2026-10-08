# app/tests/test_display_status.py
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.ordering import Table, Order, order_tables
from app.models.reservation import Reservation
from app.models.user import User, Role
from app.models.enum import TableStatus, OrderStatus, ReservationStatus
from app.services import display_status as ds_service

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
    staff = User(username="s1", email="s1@x.com", password="x", name="S1", phoneNumber="0900000001", roleID=role.id)
    customer = User(username="c1", email="c1@x.com", password="x", name="C1", phoneNumber="0900000002")
    session.add_all([staff, customer])
    session.flush()
    session.staff_id = staff.id
    session.customer_id = customer.id
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def empty_table(db):
    t = Table(number=10, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

def test_empty_table_returns_empty(db, empty_table):
    assert ds_service.compute_display_status(db, empty_table.id) == "EMPTY"

def test_table_with_active_order_returns_occupied(db, empty_table):
    order = Order(
        status=OrderStatus.CONFIRMED,
        totalPrice=100.0, subtotal=100.0, tax=0.0, delivery=0.0,
        staffID=db.staff_id, customerID=db.customer_id
    )
    db.add(order)
    db.flush()
    db.execute(order_tables.insert().values(order_id=order.id, table_id=empty_table.id))
    db.commit()
    assert ds_service.compute_display_status(db, empty_table.id) == "OCCUPIED"

def test_paying_table_returns_paying(db, empty_table):
    empty_table.status = TableStatus.PAYING
    db.commit()
    assert ds_service.compute_display_status(db, empty_table.id) == "PAYING"

def test_table_with_upcoming_reservation_returns_reserved(db, empty_table):
    soon = datetime.now(timezone.utc) + timedelta(minutes=30)
    res = Reservation(
        fullName="Test", email="t@x.com", phoneNumber="0912345678",
        numberOfGuests=2, reservationTime=soon,
        status=ReservationStatus.CONFIRMED,
        tableID=empty_table.id
    )
    db.add(res)
    db.commit()
    assert ds_service.compute_display_status(db, empty_table.id) == "RESERVED"

def test_batch_display_status(db, empty_table):
    result = ds_service.batch_display_status(db, [empty_table.id])
    assert isinstance(result, dict)
    assert result[empty_table.id] == "EMPTY"
