import pytest
from pydantic import ValidationError
from app.schemas.ordering import TableCreate
from app.schemas.layout import LayoutPayload, FloorItemCreate

def test_table_create_capacity_valid():
    tbl = TableCreate(
        number=101,
        minCapacity=2,
        seats=4,
        maxCapacity=4,
        status="EMPTY"
    )
    assert tbl.seats == 4

def test_table_create_capacity_invalid_min_greater_than_seats():
    with pytest.raises(ValidationError):
        TableCreate(
            number=102,
            minCapacity=6,
            seats=4,
            maxCapacity=6
        )

def test_table_create_capacity_invalid_seats_odd():
    with pytest.raises(ValidationError):
        TableCreate(
            number=103,
            minCapacity=2,
            seats=3,
            maxCapacity=4
        )

def test_table_create_capacity_invalid_max_capacity_exceeds_10():
    with pytest.raises(ValidationError):
        TableCreate(
            number=104,
            minCapacity=2,
            seats=8,
            maxCapacity=12
        )
