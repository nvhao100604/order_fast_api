from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        server_default=func.now(),
        index=True
    )

    updatedAt: Mapped[datetime] = mapped_column(
        "updated_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        index=True
    )