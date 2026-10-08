from app.models.enum import TableStatus, FloorItemKind, TableShape

def test_table_status_enum_values():
    assert TableStatus.PAYING.value == "PAYING"
    assert TableStatus.CLEANING.value == "CLEANING"
    assert TableStatus.RESERVED.value == "RESERVED"  # Deprecated but preserved

def test_floor_item_kind_enum_values():
    assert FloorItemKind.TABLE.value == "TABLE"
    assert FloorItemKind.PILLAR.value == "PILLAR"
    assert FloorItemKind.BAR.value == "BAR"
    assert FloorItemKind.DOOR.value == "DOOR"
    assert FloorItemKind.STAIRS.value == "STAIRS"

def test_table_shape_enum_values():
    assert TableShape.SQUARE.value == "SQUARE"
    assert TableShape.ROUND.value == "ROUND"
    assert TableShape.LONG.value == "LONG"
