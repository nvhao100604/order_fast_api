from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.enum import IdempotencyStatus


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    userID: Mapped[Optional[int]] = mapped_column("user_id", ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    requestPath: Mapped[str] = mapped_column("request_path", String(128), nullable=False)
    requestHash: Mapped[str] = mapped_column("request_hash", String(64), nullable=False)
    status: Mapped[IdempotencyStatus] = mapped_column(
        SQLEnum(IdempotencyStatus, name="idempotency_status_enum"),
        default=IdempotencyStatus.PENDING,
        server_default=IdempotencyStatus.PENDING.value,
        nullable=False,
    )
    responseCode: Mapped[Optional[int]] = mapped_column("response_code", Integer, nullable=True)
    responseBody: Mapped[Optional[str]] = mapped_column("response_body", Text, nullable=True)
    lockedUntil: Mapped[datetime] = mapped_column("locked_until", DateTime(timezone=True), nullable=False)
