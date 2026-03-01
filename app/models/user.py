from sqlalchemy import Enum, String, ForeignKey, DateTime, SmallInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
from typing import TYPE_CHECKING, List, Optional

from app.models.enum import DiscountCategory, Status

if TYPE_CHECKING:
    from .ordering import Order
    from .catalog import Dish
    from .token import RefreshToken

class Role(Base):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(String(255))
    # Liên kết với bảng User thay vì Staff cũ
    users: Mapped[List["User"]] = relationship(back_populates="internalRole")

class User(Base):
    __tablename__ = "users"
    
    # --- Thông tin chung cho Auth ---
    username: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    password: Mapped[str] = mapped_column(String(255))
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.ACTIVE)
    
    # --- Thông tin cá nhân ---
    name: Mapped[str] = mapped_column(String(255))
    phoneNumber: Mapped[str] = mapped_column(String(10), index=True, unique=True)
    
    # --- Thông tin riêng cho từng loại (để Optional) ---
    address: Mapped[Optional[str]] = mapped_column(String(255)) # Dùng cho Customer
    
    roleID: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id")) 
    internalRole: Mapped[Optional["Role"]] = relationship(back_populates="users")

    # --- Quan hệ chung ---
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    reviews: Mapped[List["Review"]] = relationship(back_populates="user")
    refreshTokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class Discount(Base):
    __tablename__ = "discount"
    category: Mapped[DiscountCategory] = mapped_column(Enum(DiscountCategory), nullable=True)
    dateBegin: Mapped[datetime] = mapped_column(DateTime)
    dateEnd: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.ACTIVE)

class Review(Base):
    __tablename__ = "reviews"
    rating: Mapped[int] = mapped_column(SmallInteger)
    comment: Mapped[str] = mapped_column(String(255))
    
    # Liên kết tới User thay vì Customer cũ
    userID: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="reviews")

    dishID: Mapped[int] = mapped_column(ForeignKey("dish.id"))
    dish: Mapped["Dish"] = relationship(back_populates="reviews")