# app/tests/test_table_ops_service.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.ordering import Table
from app.models.enum import TableStatus
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
