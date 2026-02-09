from sqlalchemy import Float, String, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.db.base import Base
import enum
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .account import Staff
    from .customer import Customer, Discount
    from .catalog import Dish

class TableStatus(enum.Enum):
    Empty = "Empty"
    Booked = "Booked"
    Deleted = "Deleted"
    Taken = "Taken"

class OrderStatus(enum.Enum):
    PENDING = "Pending confirmation"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERY_SUCCESSFUL = "Delivery Successful"
    CANCELLED = "Cancelled"
    PENDING_PAYMENT = "Pending Payment"

class Table(Base):
    __tablename__ = "tables"
    status: Mapped[TableStatus] = mapped_column(Enum(TableStatus), default=TableStatus.Empty)
    orders: Mapped[List["Order"]] = relationship(back_populates="table")

class Order(Base):
    __tablename__ = "orders"
    dateOrder: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        index=True
    )
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    totalPrice: Mapped[float] = mapped_column(Float)
    subtotal: Mapped[float] = mapped_column(Float)
    tax: Mapped[float] = mapped_column(Float)
    delivery: Mapped[float] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(String(255))
    
    staffID: Mapped[int] = mapped_column(ForeignKey("staff.id"))
    customerID: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    tableID: Mapped[int | None] = mapped_column(ForeignKey("tables.id"), nullable=True)
    discountID: Mapped[Optional[int]] = mapped_column(ForeignKey("discount.id"))
    
    staff: Mapped["Staff"] = relationship(back_populates="orders")
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    table: Mapped["Table"] = relationship(back_populates="orders")
    details: Mapped[List["OrderDetail"]] = relationship(back_populates="order")

class OrderDetail(Base):
    __tablename__ = "order_detail"
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    
    orderID: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    dishID: Mapped[int] = mapped_column(ForeignKey("dish.id"))
    
    order: Mapped["Order"] = relationship(back_populates="details")
    dish: Mapped["Dish"] = relationship(back_populates="order_details")