from sqlalchemy import Enum, String, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING, List

from app.models.enum import Status

if TYPE_CHECKING:
    from .ordering import OrderDetail
    from .user import Review

class Category(Base):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(String(255))
    dishes: Mapped[List["Dish"]] = relationship(back_populates="category")

class Dish(Base):
    __tablename__ = "dish"
    
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    imgUrl: Mapped[str] = mapped_column(String(255))
    describe: Mapped[str] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(
        Enum(Status), default=Status.ACTIVE)
    
    categoryID: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="dishes")
    order_details: Mapped[List["OrderDetail"]] = relationship(back_populates="dish")
    reviews: Mapped[List["Review"]] = relationship(back_populates="dish")