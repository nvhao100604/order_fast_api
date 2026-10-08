# app/tests/test_reservation_tables_model.py
from app.models.reservation import Reservation, reservation_tables
from app.models.ordering import Table
from sqlalchemy import inspect

def test_reservation_tables_association_table_exists():
    """reservation_tables association table must exist and have correct columns."""
    cols = {c.name for c in reservation_tables.columns}
    assert "reservation_id" in cols
    assert "table_id" in cols

def test_reservation_has_tables_relationship():
    """Reservation model must expose a .tables Many-to-Many relationship."""
    mapper = inspect(Reservation)
    assert "tables" in {r.key for r in mapper.relationships}
