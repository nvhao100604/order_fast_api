from sqlalchemy import String, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .ordering import Order

class Role(Base):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(String(255))
    staffs: Mapped[List["Staff"]] = relationship(back_populates="role")

class Staff(Base):
    __tablename__ = "staff"
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    phoneNumber: Mapped[str] = mapped_column(String(10))
    username: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    
    roleID: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(back_populates="staffs")
    orders: Mapped[List["Order"]] = relationship(back_populates="staff")