import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.ordering import Table
from app.models.layout import Area, FloorItem
from app.models.enum import TableStatus, FloorItemKind, TableShape
from app.services import layout as layout_service
from app.crud import table as table_crud
from app.schemas.layout import LayoutPayload, FloorItemCreate

SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_save_layout_optimistic_locking_conflict(db):
    area = Area(name="Khu A", gridW=30, gridH=20, layoutVersion=1)
    db.add(area)
    db.commit()
    db.refresh(area)

    payload = LayoutPayload(
        layoutVersion=999,  # Wrong version
        items=[]
    )
    with pytest.raises(HTTPException) as exc_info:
        layout_service.save_area_layout(db, area.id, payload)
    assert exc_info.value.status_code == 409

def test_save_layout_rotation_boundary_exceeded(db):
    # Area grid is 5x10
    area = Area(name="Khu Hẹp", gridW=5, gridH=10, layoutVersion=1)
    db.add(area)
    db.commit()
    db.refresh(area)

    # Item w=2, h=4. If rotation=90, effective dimensions are w=4, h=2.
    # At x=2, effective right edge = 2 + 4 = 6 > gridW (5), so it must exceed bounds.
    # (Without rotation support, x + w = 2 + 2 = 4 <= 5 would incorrectly pass).
    item = FloorItemCreate(
        kind=FloorItemKind.TABLE,
        shape=TableShape.LONG,
        x=2,
        y=0,
        w=2,
        h=4,
        rotation=90
    )
    payload = LayoutPayload(layoutVersion=1, items=[item])

    with pytest.raises(HTTPException) as exc_info:
        layout_service.save_area_layout(db, area.id, payload)
    assert exc_info.value.status_code == 422
    assert "exceeds grid bounds" in exc_info.value.detail

def test_save_layout_rotation_collision(db):
    area = Area(name="Khu Test", gridW=30, gridH=20, layoutVersion=1)
    db.add(area)
    db.commit()
    db.refresh(area)

    # Item 1: at (0, 0), w=2, h=4, rotation=90 => effective x: [0, 4), y: [0, 2)
    # Item 2: at (3, 0), w=2, h=2, rotation=0  => effective x: [3, 5), y: [0, 2)
    # They collide on x in [3, 4).
    # (Without rotation support, item 1 right edge = 2 <= item 2 left edge 3 => would incorrectly pass).
    item1 = FloorItemCreate(
        kind=FloorItemKind.TABLE,
        x=0,
        y=0,
        w=2,
        h=4,
        rotation=90
    )
    item2 = FloorItemCreate(
        kind=FloorItemKind.TABLE,
        x=3,
        y=0,
        w=2,
        h=2,
        rotation=0
    )
    payload = LayoutPayload(layoutVersion=1, items=[item1, item2])

    with pytest.raises(HTTPException) as exc_info:
        layout_service.save_area_layout(db, area.id, payload)
    assert exc_info.value.status_code == 422
    assert "collision detected" in exc_info.value.detail

def test_save_layout_syncs_table_area_id(db):
    area1 = Area(name="Khu 1", gridW=30, gridH=20, layoutVersion=1)
    area2 = Area(name="Khu 2", gridW=30, gridH=20, layoutVersion=1)
    t1 = Table(number=1, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY, areaID=1)
    t2 = Table(number=2, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY, areaID=None)
    db.add_all([area1, area2, t1, t2])
    db.commit()

    # Save layout for area 1 with ONLY t2 (t1 is removed from area 1, t2 is added to area 1)
    payload = LayoutPayload(
        layoutVersion=1,
        items=[
            FloorItemCreate(
                tableId=t2.id,
                kind=FloorItemKind.TABLE,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=0
            )
        ]
    )
    layout_service.save_area_layout(db, area1.id, payload)

    db.refresh(t1)
    db.refresh(t2)
    # t2 is placed in area 1 -> t2.areaID must be area1.id
    assert t2.areaID == area1.id
    # t1 was removed from area 1 -> t1.areaID must be None (returned to unplaced pool)
    assert t1.areaID is None

def test_update_table_removes_floor_item_when_area_changed(db):
    area1 = Area(name="Khu 1", gridW=30, gridH=20, layoutVersion=1)
    area2 = Area(name="Khu 2", gridW=30, gridH=20, layoutVersion=1)
    t = Table(number=10, minCapacity=2, seats=4, maxCapacity=4, status=TableStatus.EMPTY, areaID=1)
    db.add_all([area1, area2, t])
    db.commit()

    # Place t in area 1
    fi = FloorItem(areaID=area1.id, tableID=t.id, kind=FloorItemKind.TABLE, x=0, y=0, w=2, h=2, rotation=0)
    db.add(fi)
    db.commit()

    assert db.query(FloorItem).filter(FloorItem.tableID == t.id).first() is not None

    # Update table's areaID to area 2
    table_crud.update_table(db, t.id, {"areaID": area2.id})

    # FloorItem in area 1 should be cleaned up
    assert db.query(FloorItem).filter(FloorItem.tableID == t.id).first() is None

