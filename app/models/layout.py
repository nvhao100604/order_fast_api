from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enum import FloorItemKind, TableShape

if TYPE_CHECKING:
    from app.models.ordering import Table

class Area(Base):
    __tablename__ = "areas"

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    gridW: Mapped[int] = mapped_column("grid_w", Integer, default=30, server_default="30", nullable=False)
    gridH: Mapped[int] = mapped_column("grid_h", Integer, default=20, server_default="20", nullable=False)
    layoutVersion: Mapped[int] = mapped_column("layout_version", Integer, default=1, server_default="1", nullable=False)

    tables: Mapped[List["Table"]] = relationship("Table", back_populates="area")
    floorItems: Mapped[List["FloorItem"]] = relationship("FloorItem", back_populates="area", cascade="all, delete-orphan")

class FloorItem(Base):
    __tablename__ = "floor_items"

    areaID: Mapped[int] = mapped_column("area_id", ForeignKey("areas.id", ondelete="CASCADE"), nullable=False)
    tableID: Mapped[Optional[int]] = mapped_column("table_id", ForeignKey("tables.id", ondelete="SET NULL"), nullable=True)
    
    kind: Mapped[FloorItemKind] = mapped_column(SQLEnum(FloorItemKind), nullable=False)
    shape: Mapped[Optional[TableShape]] = mapped_column(SQLEnum(TableShape), nullable=True)

    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    w: Mapped[int] = mapped_column(Integer, nullable=False)
    h: Mapped[int] = mapped_column(Integer, nullable=False)
    rotation: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    area: Mapped["Area"] = relationship("Area", back_populates="floorItems")
    table: Mapped[Optional["Table"]] = relationship("Table", back_populates="floorItem")
