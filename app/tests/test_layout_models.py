from app.models.ordering import Table
from app.models.layout import Area, FloorItem
from app.models.enum import FloorItemKind, TableShape, TableStatus

def test_area_model_attributes():
    area = Area(name="Tầng 1", gridW=30, gridH=20, layoutVersion=1)
    assert area.name == "Tầng 1"
    assert area.gridW == 30
    assert area.gridH == 20
    assert area.layoutVersion == 1

def test_table_extended_attributes():
    table = Table(
        number=101,
        minCapacity=2,
        seats=4,
        maxCapacity=4,
        status=TableStatus.EMPTY,
        name="Bàn VIP 1",
        clusterKey="A",
        isFixed=False,
        walkInOnly=False
    )
    assert table.name == "Bàn VIP 1"
    assert table.seats == 4
    assert table.clusterKey == "A"
    assert table.isFixed is False
    assert table.walkInOnly is False

def test_floor_item_attributes():
    item = FloorItem(
        areaID=1,
        tableID=10,
        kind=FloorItemKind.TABLE,
        shape=TableShape.SQUARE,
        x=2,
        y=4,
        w=2,
        h=2,
        rotation=0
    )
    assert item.kind == FloorItemKind.TABLE
    assert item.shape == TableShape.SQUARE
    assert item.x == 2
    assert item.w == 2
