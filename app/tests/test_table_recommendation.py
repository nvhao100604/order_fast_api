# app/tests/test_table_recommendation.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.ordering import Table
from app.models.layout import Area
from app.models.enum import TableStatus
from app.services import table_recommendation as rec_service

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

def test_recommend_single_table_fits(db):
    t1 = Table(number=1, minCapacity=1, seats=2, maxCapacity=2, status=TableStatus.EMPTY)
    t2 = Table(number=2, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    t3 = Table(number=3, minCapacity=4, seats=8, maxCapacity=8, status=TableStatus.EMPTY)
    db.add_all([t1, t2, t3])
    db.commit()

    # For 3 guests, t2 fits (seats 4) tightest
    recs = rec_service.recommend_tables(db, guest_count=3)
    assert len(recs) == 1
    assert recs[0].id == t2.id

def test_recommend_combination_when_no_single_table_fits(db):
    t1 = Table(number=10, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    t2 = Table(number=11, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    db.add_all([t1, t2])
    db.commit()

    # For 7 guests, single tables (4) aren't enough, combination t1+t2 (total 8) recommended
    recs = rec_service.recommend_tables(db, guest_count=7)
    assert len(recs) == 2
    assert {t.id for t in recs} == {t1.id, t2.id}
