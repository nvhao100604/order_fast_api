from datetime import datetime
from typing import List, Optional
from .base import BaseSchema
from app.models.ordering import TableStatus, OrderStatus

class TableResponse(BaseSchema):
    id: int
    status: TableStatus

class OrderDetailBase(BaseSchema):
    dishID: int
    quantity: int
    price: float

class OrderDetailResponse(OrderDetailBase):
    id: int
    orderID: int

class OrderCreate(BaseSchema):
    staffID: int
    customerID: int
    tableID: int
    totalPrice: float
    notes: Optional[str] = None
    details: List[OrderDetailBase]

class OrderResponse(BaseSchema):
    id: int
    dateOrder: datetime
    status: OrderStatus
    totalPrice: float
    notes: Optional[str]
    details: List[OrderDetailResponse]