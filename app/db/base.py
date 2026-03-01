from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        index=True)