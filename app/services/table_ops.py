# app/services/table_ops.py
import uuid
from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ordering import Table, Order, order_tables
from app.models.enum import TableStatus, OrderStatus

_ACTIVE_ORDER_STATUSES = {
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED,
    OrderStatus.PREPARING,
    OrderStatus.SHIPPING,
    OrderStatus.UNPAID,
}


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
    """Remove clusterKey from a single table (detach from merged cluster).

    - Raises 400 if table is not part of any merged cluster.
    - Raises 409 if any table in the cluster has an active order.
    - Resets detached table's clusterKey to None and status to EMPTY.
    - If only 1 table remains in the cluster, resets that table's clusterKey to None and status to EMPTY.
    """
    table = _lock_table(db, table_id)
    if not table.clusterKey:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table {table_id} is not part of any merged cluster"
        )

    cluster_key = table.clusterKey

    # Find all tables in the cluster
    cluster_tables = db.query(Table).filter(Table.clusterKey == cluster_key).all()
    cluster_table_ids = [t.id for t in cluster_tables]

    # Check for active orders linked to any table in this cluster
    active_order = (
        db.query(Order)
        .join(order_tables, Order.id == order_tables.c.order_id)
        .filter(
            order_tables.c.table_id.in_(cluster_table_ids),
            Order.status.in_(_ACTIVE_ORDER_STATUSES)
        )
        .first()
    )
    if not active_order:
        active_order = (
            db.query(Order)
            .filter(
                Order.tableID.in_(cluster_table_ids),
                Order.status.in_(_ACTIVE_ORDER_STATUSES)
            )
            .first()
        )

    if active_order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot split table while cluster has an active order. Please complete or cancel the order first."
        )

    # Detach this table
    table.clusterKey = None
    table.status = TableStatus.EMPTY

    # If only 1 table remains in the cluster, clear its clusterKey and reset to EMPTY
    remaining_tables = [t for t in cluster_tables if t.id != table_id]
    if len(remaining_tables) == 1:
        remaining_table = remaining_tables[0]
        remaining_table.clusterKey = None
        remaining_table.status = TableStatus.EMPTY

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
