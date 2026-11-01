# app/tests/test_table_ops_service.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.ordering import Table, Order, order_tables
from app.models.enum import TableStatus, OrderStatus
from fastapi import HTTPException
from app.services import table_ops

SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def table_in_db(db):
    t = Table(number=1, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

def test_open_table_sets_occupied(db, table_in_db):
    updated = table_ops.open_table(db, table_in_db.id)
    assert updated.status == TableStatus.OCCUPIED

def test_open_table_raises_409_if_already_occupied(db, table_in_db):
    from fastapi import HTTPException
    table_ops.open_table(db, table_in_db.id)
    with pytest.raises(HTTPException) as exc:
        table_ops.open_table(db, table_in_db.id)
    assert exc.value.status_code == 409

def test_merge_tables_sets_same_cluster_key(db):
    t1 = Table(number=2, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    t2 = Table(number=3, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    db.add_all([t1, t2])
    db.commit()
    merged = table_ops.merge_tables(db, [t1.id, t2.id])
    assert merged[0].clusterKey == merged[1].clusterKey
    assert merged[0].clusterKey is not None

def test_split_table_clears_cluster_key(db):
    t1 = Table(number=4, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.OCCUPIED, clusterKey="ABC12345")
    db.add(t1)
    db.commit()
    result = table_ops.split_table(db, t1.id)
    assert result.clusterKey is None

def test_close_table_sets_cleaning(db, table_in_db):
    table_ops.open_table(db, table_in_db.id)
    result = table_ops.close_table(db, table_in_db.id)
    assert result.status == TableStatus.CLEANING


def test_split_table_raises_400_if_not_in_cluster(db):
    t = Table(number=10, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY, clusterKey=None)
    db.add(t)
    db.commit()
    with pytest.raises(HTTPException) as exc:
        table_ops.split_table(db, t.id)
    assert exc.value.status_code == 400


def test_split_table_raises_409_if_active_order(db):
    t1 = Table(number=20, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.OCCUPIED, clusterKey="ORDCLUS1")
    t2 = Table(number=21, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.OCCUPIED, clusterKey="ORDCLUS1")
    db.add_all([t1, t2])
    db.commit()

    order = Order(
        customerID=1,
        staffID=1,
        tableID=t1.id,
        subtotal=100.0,
        tax=10.0,
        delivery=0.0,
        totalPrice=110.0,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.commit()
    db.execute(order_tables.insert().values(order_id=order.id, table_id=t1.id))
    db.commit()

    with pytest.raises(HTTPException) as exc:
        table_ops.split_table(db, t1.id)
    assert exc.value.status_code == 409


def test_split_table_in_two_table_cluster_resets_both(db):
    t1 = Table(number=30, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.OCCUPIED, clusterKey="PAIR1234")
    t2 = Table(number=31, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.OCCUPIED, clusterKey="PAIR1234")
    db.add_all([t1, t2])
    db.commit()

    split_res = table_ops.split_table(db, t1.id)
    assert split_res.clusterKey is None
    assert split_res.status == TableStatus.EMPTY

    db.refresh(t2)
    assert t2.clusterKey is None
    assert t2.status == TableStatus.EMPTY


def test_split_table_in_three_table_cluster_keeps_remaining(db):
    t1 = Table(number=40, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.OCCUPIED, clusterKey="TRIPLE12")
    t2 = Table(number=41, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.OCCUPIED, clusterKey="TRIPLE12")
    t3 = Table(number=42, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.OCCUPIED, clusterKey="TRIPLE12")
    db.add_all([t1, t2, t3])
    db.commit()

    split_res = table_ops.split_table(db, t1.id)
    assert split_res.clusterKey is None
    assert split_res.status == TableStatus.EMPTY

    db.refresh(t2)
    db.refresh(t3)
    assert t2.clusterKey == "TRIPLE12"
    assert t3.clusterKey == "TRIPLE12"
