from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    Integer,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.db.base import Base
from app.models.enum import ReservationStatus

if TYPE_CHECKING:
    from app.models import User, Table


class Reservation(Base):
    __tablename__ = "reservations"

    fullName: Mapped[str] = mapped_column(
        "full_name",
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    phoneNumber: Mapped[str] = mapped_column(
        "phone_number",
        String(10),
        index=True,
        nullable=False,
    )

    numberOfGuests: Mapped[int] = mapped_column(
        "number_of_guests",
        Integer,
        nullable=False,
    )

    reservationTime: Mapped[datetime] = mapped_column(
        "reservation_time",
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )

    specialRequests: Mapped[Optional[str]] = mapped_column(
        "special_requests",
        String(255),
    )

    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(
            ReservationStatus,
            name="reservation_status_enum",
        ),
        default=ReservationStatus.PENDING,
        server_default=ReservationStatus.PENDING.value,
        nullable=False,
    )

    userID: Mapped[Optional[int]] = mapped_column(
        "user_id",
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    user: Mapped[Optional["User"]] = relationship(
        back_populates="reservations"
    )

    tableID: Mapped[Optional[int]] = mapped_column(
        "table_id",
        ForeignKey("tables.id", ondelete="SET NULL"),
        nullable=True,
    )

    table: Mapped[Optional["Table"]] = relationship(
        back_populates="reservations"
    )