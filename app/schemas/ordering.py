from datetime import datetime
from typing import List, Optional

from app.schemas.dish import DishDetail
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
    dish: DishDetail

class Total(BaseSchema):
    subtotal: float
    tax: float
    delivery: float
    total: float
    
class OrderCreate(BaseSchema):
    staffID: int
    customerID: int
    tableID: Optional[int] = None
    totalPrice: Total
    notes: Optional[str] = None
    details: List[OrderDetailBase]

class OrderResponse(BaseSchema):
    id: int
    dateOrder: datetime
    status: OrderStatus
    totalPrice: float
    notes: Optional[str]
    details: List[OrderDetailResponse]
    createdAt: datetime
    updatedAt: datetime

class OrderFilter(BaseSchema):
    dateOrder: Optional[datetime] = None
    status: Optional[OrderStatus] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    staffID: Optional[int] = None
    customerID: Optional[int] = None
    tableID: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None