from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base 

if TYPE_CHECKING:
    from .user import User

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    userAgent: Mapped[Optional[str]] = mapped_column("user_agent", String(255), nullable=True)
    expiresAt: Mapped[datetime] = mapped_column("expires_at", DateTime, nullable=False)

    userId: Mapped[Optional[int]] = mapped_column(
        "user_id", 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True
    )
    user: Mapped[Optional["User"]] = relationship(back_populates="refreshTokens")