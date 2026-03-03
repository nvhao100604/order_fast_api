from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.ordering import Table
from app.models.enum import TableStatus

def get_all_tables(db: Session, skip: int = 0, limit: int = 10):
    """Truy vấn tất cả bàn từ DB kèm phân trang"""
    tables = db.query(Table).offset(skip).limit(limit).all()
    total = db.query(func.count(Table.id)).scalar()
    return tables, total

def get_tables(db: Session, filters: dict, skip: int = 0, limit: int = 10):
    """Truy vấn danh sách bàn có lọc (status, capacity, number) và phân trang"""
    query = db.query(Table)

    if "status" in filters and filters["status"]:
        query = query.filter(Table.status == filters["status"])

    if "number" in filters and filters["number"] is not None:
        query = query.filter(Table.number == filters["number"])

    if "minCapacity" in filters and filters["minCapacity"]:
        query = query.filter(Table.maxCapacity >= filters["minCapacity"])

    query = query.order_by(Table.number.asc())

    total = query.count()
    tables = query.offset(skip).limit(limit).all()

    return tables, total

def get_table(db: Session, table_id: int):
    """Truy vấn bàn theo ID"""
    return db.query(Table).filter(Table.id == table_id).first()

def post_table(db: Session, table: Table):
    """Thêm bàn mới vào database"""
    db.add(table)
    db.commit()
    db.refresh(table)
    return table

def update_table(db: Session, table_id: int, updated_fields: dict):
    """Cập nhật một số trường của bàn theo ID (status, capacity, number, v.v.)"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if table:
        for key, value in updated_fields.items():
            if hasattr(table, key):
                setattr(table, key, value)
        db.commit()
        db.refresh(table)
    return table

def delete_table(db: Session, table_id: int):
    """Xoá bàn khỏi database theo ID"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if table:
        db.delete(table)
        db.commit()
        return table
    return None