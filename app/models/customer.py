from sqlalchemy import String, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .ordering import Order
    from .catalog import Dish

class Customer(Base):
    __tablename__ = "customer"
    name: Mapped[str] = mapped_column(String(255))
    phoneNumber: Mapped[str] = mapped_column(String(10), index=True, unique=True)
    orders: Mapped[List["Order"]] = relationship(back_populates="customer")
    reviews: Mapped[List["Review"]] = relationship(back_populates="customer")

class Discount(Base):
    __tablename__ = "discount"
    dateBegin: Mapped[datetime] = mapped_column(DateTime)
    dateEnd: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)

class Review(Base):
    __tablename__ = "reviews"
    rating: Mapped[int] = mapped_column(SmallInteger)
    comment: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    customerID: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    dishID: Mapped[int] = mapped_column(ForeignKey("dish.id"))
    
    customer: Mapped["Customer"] = relationship(back_populates="reviews")
    dish: Mapped["Dish"] = relationship(back_populates="reviews")