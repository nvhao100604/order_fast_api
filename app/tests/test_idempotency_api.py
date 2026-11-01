# app/tests/test_idempotency_api.py
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db, get_current_user
from app.db.base import Base
from app.main import app
from app.models.enum import TableStatus
from app.models.ordering import Table
from app.models.catalog import Dish
from app.models.user import User


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    current_test_user = User(id=1, username="cust", email="c@test.com", password="pwd", name="Cust", phoneNumber="0900000000", roleID=3)
    app.dependency_overrides[get_current_user] = lambda: current_test_user
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


def test_reservation_idempotent_replay(client, db):
    body = {
        "fullName": "Test User",
        "email": "test@example.com",
        "phoneNumber": "0900000000",
        "numberOfGuests": 2,
        "reservationTime": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
    }
    headers = {"Idempotency-Key": "my-uuid-key-1"}

    # 1. First request
    res1 = client.post("/api/v1/reservations", json=body, headers=headers)
    assert res1.status_code == 201
    assert res1.headers.get("X-Cache-Lookup") == "MISS"
    data1 = res1.json()

    # 2. Second request with same key
    res2 = client.post("/api/v1/reservations", json=body, headers=headers)
    assert res2.status_code == 201
    assert res2.headers.get("X-Cache-Lookup") == "HIT"
    data2 = res2.json()
    assert data1["data"]["id"] == data2["data"]["id"]


def test_order_idempotent_replay(client, db):
    dish = Dish(name="Pasta", price=50.0, imgUrl="img", describe="desc", categoryID=1)
    table = Table(number=99, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    db.add_all([dish, table])
    db.commit()

    order_body = {
        "customerID": 1,
        "tableID": table.id,
        "subtotal": 50.0,
        "tax": 5.0,
        "delivery": 0.0,
        "totalPrice": 55.0,
        "details": [{"dishID": dish.id, "quantity": 1, "price": 50.0}]
    }
    headers = {"Idempotency-Key": "order-uuid-key-2"}

    # 1. First order request
    res1 = client.post("/api/v1/orders", json=order_body, headers=headers)
    assert res1.status_code == 201
    assert res1.headers.get("X-Cache-Lookup") == "MISS"
    data1 = res1.json()

    # 2. Second order request with same key (should not trigger 409 occupied table, should replay cached response!)
    res2 = client.post("/api/v1/orders", json=order_body, headers=headers)
    assert res2.status_code == 201
    assert res2.headers.get("X-Cache-Lookup") == "HIT"
    data2 = res2.json()
    assert data1["data"]["id"] == data2["data"]["id"]

