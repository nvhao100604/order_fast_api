# app/tests/test_order_concurrency.py
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.enum import TableStatus, OrderStatus
from app.models.ordering import Table
from app.models.catalog import Dish
from app.models.user import User
from app.schemas.ordering import OrderCreate, OrderDetailBase
from app.services.order import post_order


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_concurrent_order_on_same_table_raises_409(db):
    user = User(username="cust", email="c@test.com", password="pwd", name="Cust", phoneNumber="0911111111", roleID=3)
    dish = Dish(name="Pizza", price=100.0, imgUrl="img", describe="desc", categoryID=1)
    table = Table(number=5, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY)
    db.add_all([user, dish, table])
    db.commit()

    order_in_1 = OrderCreate(
        staffID=1, customerID=user.id, tableID=table.id,
        subtotal=100.0, tax=10.0, delivery=0.0, totalPrice=110.0,
        details=[OrderDetailBase(dishID=dish.id, quantity=1, price=100.0)]
    )
    post_order(db=db, order_in=order_in_1)

    # Second order on table 5 while first order is still PENDING
    order_in_2 = OrderCreate(
        staffID=1, customerID=user.id, tableID=table.id,
        subtotal=100.0, tax=10.0, delivery=0.0, totalPrice=110.0,
        details=[OrderDetailBase(dishID=dish.id, quantity=1, price=100.0)]
    )
    with pytest.raises(HTTPException) as exc:
        post_order(db=db, order_in=order_in_2)
    assert exc.value.status_code == 409
    assert "đang có đơn hàng" in exc.value.detail or "active order" in exc.value.detail.lower()
