# app/services/table_ops.py
import uuid
from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ordering import Table
from app.models.enum import TableStatus


def _lock_table(db: Session, table_id: int) -> Table:
    """Fetch table with row-level lock (FOR UPDATE). Falls back to plain query for SQLite."""
    try:
        stmt = select(Table).filter(Table.id == table_id).with_for_update()
        table = db.execute(stmt).scalar_one_or_none()
    except Exception:
        # SQLite does not support FOR UPDATE; graceful degradation in tests
        table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table {table_id} not found"
        )
    return table


def open_table(db: Session, table_id: int) -> Table:
    """Mark table OCCUPIED. Raises 409 if not in EMPTY or CLEANING state."""
    table = _lock_table(db, table_id)
    if table.status not in (TableStatus.EMPTY, TableStatus.CLEANING):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Table {table_id} cannot be opened from status '{table.status.value}'"
        )
    table.status = TableStatus.OCCUPIED
    db.commit()
    db.refresh(table)
    return table


def merge_tables(db: Session, table_ids: List[int]) -> List[Table]:
    """Assign a shared clusterKey to all given tables. Raises 409 if any is DELETED."""
    tables = []
    for tid in table_ids:
        t = _lock_table(db, tid)
        if t.status == TableStatus.DELETED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Table {tid} is DELETED and cannot be merged"
            )
        tables.append(t)

    cluster_key = uuid.uuid4().hex[:8].upper()
    for t in tables:
        t.clusterKey = cluster_key
        if t.status == TableStatus.EMPTY:
            t.status = TableStatus.OCCUPIED

    db.commit()
    for t in tables:
        db.refresh(t)
    return tables


def split_table(db: Session, table_id: int) -> Table:
    """Remove clusterKey from a single table (detach from merged cluster)."""
    table = _lock_table(db, table_id)
    table.clusterKey = None
    db.commit()
    db.refresh(table)
    return table


def close_table(db: Session, table_id: int) -> Table:
    """Mark table as CLEANING (awaiting next cycle)."""
    table = _lock_table(db, table_id)
    table.status = TableStatus.CLEANING
    db.commit()
    db.refresh(table)
    return table
