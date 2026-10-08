# app/tests/test_phase2_full.py
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from app.models.ordering import Table, Order, order_tables
from app.models.reservation import Reservation
from app.models.user import User, Role
from app.models.enum import TableStatus, OrderStatus, ReservationStatus

client = TestClient(app)
SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture
def mem_db():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _seed_users(db):
    role = Role(name="TestRole")
    db.add(role)
    db.flush()
    staff = User(username="p2_s", email="p2_s@x.com", password="x", name="P2 S", phoneNumber="0900000020", roleID=role.id)
    customer = User(username="p2_c", email="p2_c@x.com", password="x", name="P2 C", phoneNumber="0900000021")
    db.add_all([staff, customer])
    db.flush()
    return staff.id, customer.id


def test_order_tables_association_columns_exist():
    """order_tables must have order_id and table_id columns."""
    from app.models.ordering import order_tables as ot
    cols = {c.name for c in ot.columns}
    assert "order_id" in cols and "table_id" in cols


def test_table_open_then_close_lifecycle(mem_db):
    from app.services import table_ops
    t = Table(number=50, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    mem_db.add(t)
    mem_db.commit()

    opened = table_ops.open_table(mem_db, t.id)
    assert opened.status == TableStatus.OCCUPIED

    closed = table_ops.close_table(mem_db, t.id)
    assert closed.status == TableStatus.CLEANING


def test_merge_and_split_tables(mem_db):
    from app.services import table_ops
    t1 = Table(number=51, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    t2 = Table(number=52, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    mem_db.add_all([t1, t2])
    mem_db.commit()

    merged = table_ops.merge_tables(mem_db, [t1.id, t2.id])
    assert merged[0].clusterKey == merged[1].clusterKey

    split = table_ops.split_table(mem_db, t1.id)
    assert split.clusterKey is None


def test_display_status_empty(mem_db):
    from app.services import display_status as ds
    t = Table(number=60, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    mem_db.add(t)
    mem_db.commit()
    assert ds.compute_display_status(mem_db, t.id) == "EMPTY"


def test_display_status_occupied_via_order(mem_db):
    from app.services import display_status as ds
    staff_id, customer_id = _seed_users(mem_db)
    t = Table(number=61, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    mem_db.add(t)
    mem_db.flush()
    order = Order(
        status=OrderStatus.CONFIRMED,
        totalPrice=50.0, subtotal=50.0, tax=0.0, delivery=0.0,
        staffID=staff_id, customerID=customer_id
    )
    mem_db.add(order)
    mem_db.flush()
    mem_db.execute(order_tables.insert().values(order_id=order.id, table_id=t.id))
    mem_db.commit()
    assert ds.compute_display_status(mem_db, t.id) == "OCCUPIED"


def test_display_status_paying(mem_db):
    from app.services import display_status as ds
    t = Table(number=62, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.PAYING)
    mem_db.add(t)
    mem_db.commit()
    assert ds.compute_display_status(mem_db, t.id) == "PAYING"


def test_display_status_reserved(mem_db):
    from app.services import display_status as ds
    t = Table(number=63, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    mem_db.add(t)
    mem_db.commit()
    soon = datetime.now(timezone.utc) + timedelta(minutes=45)
    res = Reservation(
        fullName="R", email="r@x.com", phoneNumber="0912345680",
        numberOfGuests=2, reservationTime=soon,
        status=ReservationStatus.CONFIRMED, tableID=t.id
    )
    mem_db.add(res)
    mem_db.commit()
    assert ds.compute_display_status(mem_db, t.id) == "RESERVED"


def test_open_table_api_registered():
    r = client.post("/api/v1/tables/999/open")
    assert r.status_code in (401, 404)
    if r.status_code == 404:
        assert "Table 999 not found" in str(r.json())

def test_merge_tables_api_registered():
    r = client.post("/api/v1/tables/merge", json={"tableIDs": [998, 999]})
    assert r.status_code in (401, 404)

def test_split_table_api_registered():
    r = client.post("/api/v1/tables/999/split")
    assert r.status_code in (401, 404)
    if r.status_code == 404:
        assert "Table 999 not found" in str(r.json())

def test_close_table_api_registered():
    r = client.post("/api/v1/tables/999/close")
    assert r.status_code in (401, 404)
    if r.status_code == 404:
        assert "Table 999 not found" in str(r.json())
