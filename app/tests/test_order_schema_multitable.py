# app/tests/test_order_schema_multitable.py
import pytest
from pydantic import ValidationError
from app.schemas.ordering import OrderCreate, OrderResponse, TableStatusResponse

def test_order_create_accepts_table_ids_list():
    order = OrderCreate(
        customerID=1,
        subtotal=100.0,
        tax=10.0,
        delivery=0.0,
        totalPrice=110.0,
        details=[],
        tableIDs=[1, 2],
    )
    assert order.tableIDs == [1, 2]

def test_order_create_tableids_defaults_empty():
    order = OrderCreate(
        customerID=1,
        subtotal=50.0,
        tax=5.0,
        delivery=0.0,
        totalPrice=55.0,
        details=[],
    )
    assert order.tableIDs == []

def test_table_status_response_has_display_status():
    """TableStatusResponse must have displayStatus field."""
    fields = TableStatusResponse.model_fields
    assert "displayStatus" in fields
