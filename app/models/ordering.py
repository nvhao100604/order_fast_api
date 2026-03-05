from sqlalchemy import (
    CheckConstraint,
    String,
    ForeignKey,
    Integer,
    Numeric,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING, List, Optional

from app.models.enum import OrderStatus, TableStatus

if TYPE_CHECKING:
    from .user import User, Discount
    from .catalog import Dish
    from .reservation import Reservation


# =========================
# TABLE
# =========================
class Table(Base):
    __tablename__ = "tables"

    number: Mapped[int] = mapped_column(Integer, unique=True)

    minCapacity: Mapped[int] = mapped_column(
        "min_capacity", Integer, nullable=False
    )
    maxCapacity: Mapped[int] = mapped_column(
        "max_capacity", Integer, nullable=False
    )

    status: Mapped[TableStatus] = mapped_column(
        SQLEnum(TableStatus, name="table_status_enum"),
        default=TableStatus.EMPTY,
        server_default=TableStatus.EMPTY.value,
    )

    orders: Mapped[List["Order"]] = relationship(
        back_populates="table"
    )

    reservations: Mapped[List["Reservation"]] = relationship(
        back_populates="table"
    )

    __table_args__ = (
        CheckConstraint(
            "min_capacity > 0",
            name="check_min_capacity_positive",
        ),
        CheckConstraint(
            "max_capacity >= min_capacity",
            name="check_max_ge_min",
        ),
    )


# =========================
# ORDER
# =========================
class Order(Base):
    __tablename__ = "orders"

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_status_enum"),
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
    )

    totalPrice: Mapped[float] = mapped_column(
        "total_price", Numeric(10, 2)
    )
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2))
    tax: Mapped[float] = mapped_column(Numeric(10, 2))
    delivery: Mapped[float] = mapped_column(Numeric(10, 2))

    notes: Mapped[Optional[str]] = mapped_column(String(255))

    # Staff Mapping
    staffID: Mapped[int] = mapped_column(
        "staff_id",
        ForeignKey("users.id"),
    )
    staff: Mapped["User"] = relationship(
        "User",
        foreign_keys=[staffID],
        back_populates="staffOrders",
    )

    # Customer Mapping
    customerID: Mapped[int] = mapped_column(
        "customer_id",
        ForeignKey("users.id"),
    )
    customer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[customerID],
        back_populates="orders",
    )

    tableID: Mapped[Optional[int]] = mapped_column(
        "table_id",
        ForeignKey("tables.id"),
        nullable=True,
    )
    table: Mapped[Optional["Table"]] = relationship(
        back_populates="orders"
    )

    discountID: Mapped[Optional[int]] = mapped_column(
        "discount_id",
        ForeignKey("discount.id"),
    )
    discount: Mapped[Optional["Discount"]] = relationship(
        back_populates="orders"
    )

    details: Mapped[List["OrderDetail"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


# =========================
# ORDER DETAIL
# =========================
class OrderDetail(Base):
    __tablename__ = "order_details"

    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Numeric(10, 2))

    orderID: Mapped[int] = mapped_column(
        "order_id",
        ForeignKey("orders.id", ondelete="CASCADE"),
    )
    order: Mapped["Order"] = relationship(
        back_populates="details"
    )

    dishID: Mapped[int] = mapped_column(
        "dish_id",
        ForeignKey("dish.id"),
    )
    dish: Mapped["Dish"] = relationship(
        back_populates="orderDetails"
    )