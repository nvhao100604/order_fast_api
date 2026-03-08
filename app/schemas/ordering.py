from datetime import datetime
import string
from typing import List, Optional
from pydantic import Field

from app.schemas.dish import DishDetail
from .base import BaseSchema
from app.models.enum import OrderStatus, TableStatus

# --- Table Schemas ---
class TableBase(BaseSchema):
    number: int
    minCapacity: int
    maxCapacity: int
    status: TableStatus

class TableResponse(TableBase):
    id: int

class TableUpdate(BaseSchema):
    number: Optional[int]
    minCapacity: Optional[int]
    maxCapacity: Optional[int]
    status: Optional[TableStatus]

class TableFilter(TableUpdate):
    pass

# --- Order Detail Schemas ---

class OrderDetailBase(BaseSchema):
    dishID: int
    quantity: int
    price: float

class OrderDetailResponse(OrderDetailBase):
    id: int
    orderID: int
    dish: DishDetail

# --- Total / Pricing Schemas ---

class OrderPricing(BaseSchema):
    subtotal: float
    tax: float
    delivery: float
    totalPrice: float = Field(..., alias="totalPrice")

# --- Order Schemas ---

class OrderCreate(BaseSchema):
    staffID: Optional[int] = None
    customerID: int
    tableID: Optional[int] = None
    discountID: Optional[int] = None
    
    subtotal: float
    tax: float
    delivery: float
    totalPrice: float
    
    notes: Optional[str] = Field(None, max_length=255)
    details: List[OrderDetailBase]

class OrderResponse(BaseSchema):
    id: int
    status: OrderStatus
    
    subtotal: float
    tax: float
    delivery: float
    totalPrice: float
    
    notes: Optional[str]
    staffID: int
    customerID: int
    tableID: Optional[int]
    discountID: Optional[int]
    
    details: List[OrderDetailResponse]
    createdAt: datetime
    updatedAt: datetime

# --- Filter Schemas ---

class OrderFilter(BaseSchema):
    status: Optional[OrderStatus] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    staffID: Optional[int] = None
    customerID: Optional[int] = None
    tableID: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    customer_search: Optional[str] = None
    staff_search: Optional[str] = None