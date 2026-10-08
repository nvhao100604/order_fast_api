from datetime import datetime
import string
from typing import List, Optional
from pydantic import Field

from app.schemas.dish import DishDetail
from .base import BaseSchema
from app.models.enum import OrderStatus, TableStatus

from pydantic import Field, field_validator

# --- Table Schemas ---
class TableBase(BaseSchema):
    number: int
    name: Optional[str] = None
    minCapacity: int = 1
    seats: int = 2
    maxCapacity: int = 2
    areaId: Optional[int] = None
    clusterKey: Optional[str] = None
    isFixed: bool = False
    walkInOnly: bool = False
    status: TableStatus = TableStatus.EMPTY

    @field_validator("seats")
    @classmethod
    def validate_seats(cls, v: int) -> int:
        if v < 2 or v > 10 or v % 2 != 0:
            raise ValueError("seats must be an even number between 2 and 10")
        return v

    @field_validator("maxCapacity")
    @classmethod
    def validate_capacity_bounds(cls, max_cap: int, info) -> int:
        data = info.data
        min_cap = data.get("minCapacity", 1)
        seats = data.get("seats", 2)
        if min_cap < 1:
            raise ValueError("minCapacity must be >= 1")
        if min_cap > seats:
            raise ValueError("minCapacity must be <= seats")
        if seats > max_cap:
            raise ValueError("seats must be <= maxCapacity")
        if max_cap > 10:
            raise ValueError("maxCapacity cannot exceed 10")
        return max_cap

class TableCreate(TableBase):
    pass

class TableResponse(TableBase):
    id: int
    displayStatus: Optional[str] = None


class TableUpdate(BaseSchema):
    number: Optional[int] = None
    name: Optional[str] = None
    minCapacity: Optional[int] = None
    seats: Optional[int] = None
    maxCapacity: Optional[int] = None
    areaId: Optional[int] = None
    clusterKey: Optional[str] = None
    isFixed: Optional[bool] = None
    walkInOnly: Optional[bool] = None
    status: Optional[TableStatus] = None

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