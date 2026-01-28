from pydantic import Field
from datetime import datetime
from typing import Optional, List
from .base import BaseSchema
from app.models.customer import DiscountCategory

class CustomerBase(BaseSchema):
    name: str = Field(..., min_length=2, max_length=255)
    phoneNumber: str = Field(..., pattern=r"^\d{10}$") 

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int

class ReviewBase(BaseSchema):
    customerID: int
    dishID: int
    rating: int = Field(..., ge=1, le=5) 
    comment: str = Field(..., max_length=255)

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    created_at: datetime

class DiscountBase(BaseSchema):
    category: DiscountCategory
    dateBegin: datetime
    dateEnd: datetime
    status: int = 1

class DiscountResponse(DiscountBase):
    id: int

class DiscountDetailOrderBase(BaseSchema):
    discountID: int
    nameDiscount: str
    percent: int = Field(..., ge=0, le=100)

class DiscountDetailOrderResponse(DiscountDetailOrderBase):
    id: int