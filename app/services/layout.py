from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.layout import Area, FloorItem
from app.models.ordering import Table
from app.schemas.layout import LayoutPayload, FloorItemCreate

def get_all_areas(db: Session) -> List[Area]:
    return db.query(Area).all()

def get_area_layout(db: Session, area_id: int):
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found")
    
    items = db.query(FloorItem).filter(FloorItem.areaID == area_id).all()
    tables = db.query(Table).filter(Table.areaID == area_id, Table.status != "DELETED").all()
    return area, items, tables

def get_unplaced_tables(db: Session) -> List[Table]:
    placed_table_ids = db.query(FloorItem.tableID).filter(FloorItem.tableID.isnot(None))
    return db.query(Table).filter(
        Table.status != "DELETED",
        ~Table.id.in_(placed_table_ids)
    ).all()


def get_effective_dimensions(w: int, h: int, rotation: int = 0) -> tuple[int, int]:
    """Tính toán chiều rộng và chiều cao hiệu dụng trên lưới theo góc xoay (AABB)."""
    if (rotation % 180) != 0:
        return h, w
    return w, h


def save_area_layout(db: Session, area_id: int, payload: LayoutPayload):
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found")

    # 1. Optimistic Locking check
    if area.layoutVersion != payload.layoutVersion:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Layout version mismatch. Server has version {area.layoutVersion}, payload provided {payload.layoutVersion}"
        )

    # 2. Collision & Boundary check (với góc xoay)
    items = payload.items
    seen_tables = set()
    for i in range(len(items)):
        item1 = items[i]
        eff1_w, eff1_h = get_effective_dimensions(item1.w, item1.h, item1.rotation)

        # Check grid boundary
        if item1.x < 0 or item1.y < 0 or (item1.x + eff1_w) > area.gridW or (item1.y + eff1_h) > area.gridH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Item at ({item1.x}, {item1.y}) exceeds grid bounds ({area.gridW}x{area.gridH})"
            )
        # Duplicate table placement check
        if item1.tableId is not None:
            if item1.tableId in seen_tables:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Table ID {item1.tableId} placed multiple times in layout"
                )
            seen_tables.add(item1.tableId)

        # Overlap check with other items
        for j in range(i + 1, len(items)):
            item2 = items[j]
            eff2_w, eff2_h = get_effective_dimensions(item2.w, item2.h, item2.rotation)
            overlap = not (
                item1.x + eff1_w <= item2.x or
                item2.x + eff2_w <= item1.x or
                item1.y + eff1_h <= item2.y or
                item2.y + eff2_h <= item1.y
            )
            if overlap:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Layout items collision detected between item at ({item1.x},{item1.y}) and ({item2.x},{item2.y})"
                )

    # 3. Synchronize Table.areaID (Single Source of Truth)
    new_table_ids = {item.tableId for item in items if item.tableId is not None}

    # Các bàn từng thuộc area này nhưng bị gỡ khỏi layout -> trả về pool (areaID = None)
    tables_in_area = db.query(Table).filter(Table.areaID == area_id).all()
    for t in tables_in_area:
        if t.id not in new_table_ids:
            t.areaID = None

    # Các bàn mới được đưa vào sơ đồ area này -> dọn FloorItem cũ ở khu vực khác và cập nhật areaID = area_id
    if new_table_ids:
        db.query(FloorItem).filter(
            FloorItem.tableID.in_(new_table_ids),
            FloorItem.areaID != area_id
        ).delete(synchronize_session=False)

        placed_tables = db.query(Table).filter(Table.id.in_(new_table_ids)).all()
        for t in placed_tables:
            t.areaID = area_id

    # 4. Replace layout items and bump layoutVersion
    db.query(FloorItem).filter(FloorItem.areaID == area_id).delete(synchronize_session=False)

    for item_data in items:
        new_item = FloorItem(
            areaID=area_id,
            tableID=item_data.tableId,
            kind=item_data.kind,
            shape=item_data.shape,
            x=item_data.x,
            y=item_data.y,
            w=item_data.w,
            h=item_data.h,
            rotation=item_data.rotation
        )
        db.add(new_item)

    area.layoutVersion += 1
    db.commit()
    db.refresh(area)
    
    updated_items = db.query(FloorItem).filter(FloorItem.areaID == area_id).all()
    updated_tables = db.query(Table).filter(Table.areaID == area_id, Table.status != "DELETED").all()
    return area, updated_items, updated_tables

