from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional

from app.models.enum import Status

# --- ROLE SCHEMAS ---
class RoleBase(BaseModel):
    name: str = Field(..., max_length=255)

class RoleResponse(RoleBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

# --- REVIEW SCHEMAS ---
class ReviewBase(BaseModel):
    dishID: int
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., max_length=255)

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    userID: int 
    createdAt: datetime
    updatedAt: datetime

# --- DISCOUNT SCHEMAS ---
class DiscountBase(BaseModel):
    category: Optional[str] = None
    dateBegin: datetime
    dateEnd: datetime
    status: Status = Status.ACTIVE

class DiscountResponse(DiscountBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

class DiscountDetailOrderBase(BaseModel):
    discountID: int
    nameDiscount: str
    percent: int = Field(..., ge=0, le=100)

class DiscountDetailOrderResponse(DiscountDetailOrderBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
