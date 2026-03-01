from typing import TYPE_CHECKING, Optional
from realtime import Optional
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base 

if TYPE_CHECKING:
    from .user import User

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    userAgent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expiresAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    userID: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    user: Mapped[Optional["User"]] = relationship(back_populates="refreshTokens")