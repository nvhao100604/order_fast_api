from sqlalchemy import (
    Enum as SQLEnum,
    String,
    ForeignKey,
    Numeric,
    Text,
)
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

    dishes: Mapped[List["Dish"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )


class Dish(Base):
    __tablename__ = "dish"

    name: Mapped[str] = mapped_column(String(255))

    price: Mapped[float] = mapped_column(Numeric(10, 2))

    imgUrl: Mapped[str] = mapped_column(
        "img_url", String(255)
    )

    describe: Mapped[str] = mapped_column(Text)

    status: Mapped[Status] = mapped_column(
        SQLEnum(Status, name="dish_status_enum"),
        default=Status.ACTIVE,
        server_default=Status.ACTIVE.value,
    )

    categoryID: Mapped[int] = mapped_column(
        "category_id",
        ForeignKey("categories.id"),
    )

    category: Mapped["Category"] = relationship(
        back_populates="dishes"
    )

    orderDetails: Mapped[List["OrderDetail"]] = relationship(
        back_populates="dish"
    )

    reviews: Mapped[List["Review"]] = relationship(
        back_populates="dish"
    )