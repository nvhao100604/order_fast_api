from sqlalchemy import CheckConstraint, Float, String, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING, List, Optional

from app.models.enum import OrderStatus, TableStatus

if TYPE_CHECKING:
    from .user import User, Discount
    from .catalog import Dish
    from .reservation import Reservation

class Table(Base):
    __tablename__ = "tables"

    number: Mapped[int] = mapped_column(Integer, unique=True)
    
    minCapacity: Mapped[int] = mapped_column("min_capacity", Integer, nullable=False)
    maxCapacity: Mapped[int] = mapped_column("max_capacity", Integer, nullable=False)
    
    status: Mapped[TableStatus] = mapped_column(
        SQLEnum(TableStatus),
        default=TableStatus.EMPTY,
        server_default=TableStatus.EMPTY.value
    )
    
    orders: Mapped[List["Order"]] = relationship(back_populates="table")

    __table_args__ = (
        CheckConstraint("min_capacity > 0", name="check_min_capacity_positive"),
        CheckConstraint("max_capacity >= min_capacity", name="check_max_ge_min"),
    )

    reservations: Mapped[List["Reservation"]] = relationship(
    back_populates="table"
)

class Order(Base):
    __tablename__ = "orders"

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus), 
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value
    )
    
    totalPrice: Mapped[float] = mapped_column("total_price", Float)
    subtotal: Mapped[float] = mapped_column(Float)
    tax: Mapped[float] = mapped_column(Float)
    delivery: Mapped[float] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(String(255))
    
   # Staff Mapping
    staffID: Mapped[int] = mapped_column("staff_id", ForeignKey("users.id"))
    staff: Mapped["User"] = relationship(
        "User", foreign_keys=[staffID], back_populates="staffOrders"
    )

    # Customer Mapping
    customerID: Mapped[int] = mapped_column("customer_id", ForeignKey("users.id"))
    customer: Mapped["User"] = relationship(
        "User", foreign_keys=[customerID], back_populates="orders"
    )

    tableID: Mapped[int | None] = mapped_column("table_id", ForeignKey("tables.id"), nullable=True)
    table: Mapped["Table"] = relationship(back_populates="orders")

    discountID: Mapped[Optional[int]] = mapped_column("discount_id", ForeignKey("discount.id"))
    discount: Mapped[Optional["Discount"]] = relationship(back_populates="orders")

    details: Mapped[List["OrderDetail"]] = relationship(back_populates="order")

class OrderDetail(Base):
    __tablename__ = "order_details"
    
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    
    orderID: Mapped[int] = mapped_column("order_id", ForeignKey("orders.id"))
    order: Mapped["Order"] = relationship(back_populates="details")

    dishID: Mapped[int] = mapped_column("dish_id", ForeignKey("dish.id"))
    dish: Mapped["Dish"] = relationship(back_populates="orderDetails")