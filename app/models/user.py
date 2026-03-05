from sqlalchemy import Enum as SQLEnum, String, ForeignKey, DateTime, SmallInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
from typing import TYPE_CHECKING, List, Optional

from app.models.enum import DiscountCategory, Status

if TYPE_CHECKING:
    from .ordering import Order
    from .catalog import Dish
    from .token import RefreshToken
    from .reservation import Reservation

class Role(Base):
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(255))
    
    users: Mapped[List["User"]] = relationship(back_populates="internalRole")

class User(Base):
    __tablename__ = "users"
    
    username: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    password: Mapped[str] = mapped_column(String(255))
    
    status: Mapped[Status] = mapped_column(
        SQLEnum(Status), 
        default=Status.ACTIVE, 
        server_default=Status.ACTIVE.value
    )
    
    name: Mapped[str] = mapped_column(String(255))
    phoneNumber: Mapped[str] = mapped_column("phone_number", String(10), index=True, unique=True)
    address: Mapped[Optional[str]] = mapped_column(String(255))

    roleID: Mapped[Optional[int]] = mapped_column("role_id", ForeignKey("roles.id")) 
    internalRole: Mapped[Optional["Role"]] = relationship(back_populates="users")
    
    # 1. Đơn hàng khách đặt
    orders: Mapped[List["Order"]] = relationship(
        "Order", 
        foreign_keys="[Order.customerID]", 
        back_populates="customer"
    )
    # 2. Đơn hàng nhân viên xử lý
    staffOrders: Mapped[List["Order"]] = relationship(
        "Order", 
        foreign_keys="[Order.staffID]", 
        back_populates="staff"
    )

    reviews: Mapped[List["Review"]] = relationship(back_populates="user")
    
    refreshTokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    reservations: Mapped[List["Reservation"]] = relationship(
    back_populates="user"
)

class Discount(Base):
    __tablename__ = "discount"
    
    category: Mapped[DiscountCategory] = mapped_column(SQLEnum(DiscountCategory), nullable=True)
    
    dateBegin: Mapped[datetime] = mapped_column("date_begin", DateTime)
    dateEnd: Mapped[datetime] = mapped_column("date_end", DateTime)
    
    status: Mapped[Status] = mapped_column(
        SQLEnum(Status), 
        default=Status.ACTIVE, 
        server_default=Status.ACTIVE.value
    )

    orders: Mapped[List["Order"]] = relationship(back_populates="discount")

class Review(Base):
    __tablename__ = "reviews"
    
    rating: Mapped[int] = mapped_column(SmallInteger)
    comment: Mapped[str] = mapped_column(String(255))
    
    userID: Mapped[int] = mapped_column("user_id", ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="reviews")

    dishID: Mapped[int] = mapped_column("dish_id", ForeignKey("dish.id"))
    dish: Mapped["Dish"] = relationship(back_populates="reviews")