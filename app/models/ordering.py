from sqlalchemy import CheckConstraint, Float, String, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING, List, Optional

from app.models.enum import OrderStatus, TableStatus
from app.models.user import Discount

if TYPE_CHECKING:
    from .user import User
    from .catalog import Dish

class Table(Base):
    __tablename__ = "tables"

    number: Mapped[int] = mapped_column(Integer, unique=True)
    min_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TableStatus] = mapped_column(
        Enum(TableStatus),
        default=TableStatus.Empty
    )
    orders: Mapped[List["Order"]] = relationship(back_populates="table")

    __table_args__ = (
        CheckConstraint("min_capacity > 0", name="check_min_capacity_positive"),
        CheckConstraint("max_capacity >= min_capacity", name="check_max_ge_min"),
    )

class Order(Base):
    __tablename__ = "orders"

    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    totalPrice: Mapped[float] = mapped_column(Float)
    subtotal: Mapped[float] = mapped_column(Float)
    tax: Mapped[float] = mapped_column(Float)
    delivery: Mapped[float] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(String(255))
    
    staffID: Mapped[int] = mapped_column(ForeignKey("users.id"))
    staff: Mapped["User"] = relationship(back_populates="orders")

    customerID: Mapped[int] = mapped_column(ForeignKey("users.id"))
    customer: Mapped["User"] = relationship(back_populates="orders")

    tableID: Mapped[int | None] = mapped_column(ForeignKey("tables.id"), nullable=True)
    table: Mapped["Table"] = relationship(back_populates="orders")

    discountID: Mapped[Optional[int]] = mapped_column(ForeignKey("discount.id"))
    discount: Mapped[Optional["Discount"]] = relationship(back_populates="orders")

    details: Mapped[List["OrderDetail"]] = relationship(back_populates="order")

class OrderDetail(Base):
    __tablename__ = "order_details"
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    
    orderID: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order: Mapped["Order"] = relationship(back_populates="details")

    dishID: Mapped[int] = mapped_column(ForeignKey("dish.id"))
    dish: Mapped["Dish"] = relationship(back_populates="order_details")