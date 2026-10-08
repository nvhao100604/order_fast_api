# app/tests/test_order_tables_model.py
from app.models.ordering import Order, Table, order_tables
from sqlalchemy import inspect

def test_order_tables_association_table_exists():
    """order_tables association table must exist and have the right columns."""
    cols = {c.name for c in order_tables.columns}
    assert "order_id" in cols
    assert "table_id" in cols

def test_order_has_tables_relationship():
    """Order model must expose a .tables Many-to-Many relationship."""
    mapper = inspect(Order)
    assert "tables" in {r.key for r in mapper.relationships}

def test_table_has_linked_orders_relationship():
    """Table model must expose a .linkedOrders Many-to-Many relationship."""
    mapper = inspect(Table)
    assert "linkedOrders" in {r.key for r in mapper.relationships}
