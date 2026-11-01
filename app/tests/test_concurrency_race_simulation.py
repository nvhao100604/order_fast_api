# app/tests/test_concurrency_race_simulation.py
import concurrent.futures
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db, get_current_user
from app.db.base import Base
from app.main import app
from app.models.enum import TableStatus
from app.models.ordering import Table
from app.models.catalog import Dish
from app.models.reservation import Reservation
from app.models.user import User


@pytest.fixture
def file_db_setup(tmp_path):
    db_file = tmp_path / "test_concurrency.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False, "timeout": 30}
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    # Seed test table, dish, user
    init_session = TestingSession()
    table = Table(number=777, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    dish = Dish(name="Steak", price=120.0, imgUrl="img", describe="desc", categoryID=1)
    user = User(username="cust1", email="c1@test.com", password="pwd", name="Cust", phoneNumber="0900000000", roleID=3)
    init_session.add_all([table, dish, user])
    init_session.commit()
    table_id = table.id
    dish_id = dish.id
    user_id = user.id
    init_session.close()

    yield engine, TestingSession, table_id, dish_id, user_id
    Base.metadata.drop_all(bind=engine)


def test_table_overlap_conflict_rejection(file_db_setup):
    """Verify that once a table is reserved, another booking in overlapping window is rejected with 409."""
    engine, TestingSession, table_id, _, _ = file_db_setup

    def get_test_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_test_db
    client = TestClient(app)
    slot = datetime(2030, 8, 1, 19, 0, tzinfo=timezone.utc)

    # First booking succeeds
    res1 = client.post("/api/v1/reservations", json={
        "fullName": "User First",
        "email": "first@test.com",
        "phoneNumber": "0900000001",
        "numberOfGuests": 2,
        "reservationTime": slot.isoformat(),
        "tableID": table_id
    })
    assert res1.status_code == 201

    # Second booking 30m later for same table fails with 409 Conflict
    res2 = client.post("/api/v1/reservations", json={
        "fullName": "User Second",
        "email": "second@test.com",
        "phoneNumber": "0900000002",
        "numberOfGuests": 2,
        "reservationTime": (slot + timedelta(minutes=30)).isoformat(),
        "tableID": table_id
    })
    assert res2.status_code == 409
    body_data = res2.json()
    assert "đã có khách đặt" in (body_data.get("message") or body_data.get("detail", ""))



def test_concurrent_double_click_reservation_idempotency(file_db_setup):
    """Verify double-clicking reservation button with same Idempotency-Key creates exactly 1 booking."""
    engine, TestingSession, table_id, _, _ = file_db_setup

    def get_test_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_test_db
    slot = datetime(2030, 9, 1, 19, 0, tzinfo=timezone.utc)
    body = {
        "fullName": "User DoubleClick",
        "email": "dc@test.com",
        "phoneNumber": "0900000003",
        "numberOfGuests": 2,
        "reservationTime": slot.isoformat(),
        "tableID": table_id
    }
    headers = {"Idempotency-Key": "double-click-res-key-99"}

    def attempt_res(idx):
        client = TestClient(app)
        res = client.post("/api/v1/reservations", json=body, headers=headers)
        return res.status_code, res.headers.get("X-Cache-Lookup")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt_res, range(2)))

    status_codes = [r[0] for r in results]
    assert all(code in (201, 409) for code in status_codes)
    assert 201 in status_codes

    # Exactly 1 reservation created in DB
    verify_session = TestingSession()
    res_count = verify_session.query(Reservation).filter(Reservation.email == "dc@test.com").count()
    verify_session.close()
    assert res_count == 1


def test_concurrent_double_click_order_idempotency(file_db_setup):
    """Verify double-clicking order button with same Idempotency-Key creates exactly 1 order."""
    engine, TestingSession, table_id, dish_id, user_id = file_db_setup

    def get_test_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_test_db
    current_test_user = User(id=user_id, username="cust1", email="c1@test.com", password="pwd", name="Cust", phoneNumber="0900000000", roleID=3)
    app.dependency_overrides[get_current_user] = lambda: current_test_user

    order_body = {
        "customerID": user_id,
        "tableID": table_id,
        "subtotal": 120.0,
        "tax": 12.0,
        "delivery": 0.0,
        "totalPrice": 132.0,
        "details": [{"dishID": dish_id, "quantity": 1, "price": 120.0}]
    }
    headers = {"Idempotency-Key": "shared-double-click-key-1"}

    def attempt_order(idx):
        client = TestClient(app)
        res = client.post("/api/v1/orders", json=order_body, headers=headers)
        return res.status_code, res.headers.get("X-Cache-Lookup")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt_order, range(2)))

    status_codes = [r[0] for r in results]
    assert all(code in (201, 409) for code in status_codes)
    assert 201 in status_codes
