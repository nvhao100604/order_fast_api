from datetime import datetime
from typing import Optional
from pydantic import Field, EmailStr
from app.schemas.base import BaseSchema
from app.models.enum import ReservationStatus


class ReservationBase(BaseSchema):
    fullName: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phoneNumber: str = Field(..., pattern=r"^\d{10}$")
    numberOfGuests: int = Field(..., gt=0)
    reservationTime: datetime
    specialRequests: Optional[str] = Field(None, max_length=255)

class ReservationCreate(ReservationBase):
    userID: Optional[int] = None

class ReservationUpdate(BaseSchema):
    numberOfGuests: Optional[int] = None
    reservationTime: Optional[datetime] = None
    specialRequests: Optional[str] = None
    status: Optional[ReservationStatus] = None
    tableID: Optional[int] = None

class ReservationResponse(ReservationBase):
    id: int
    status: ReservationStatus
    userID: Optional[int]
    tableID: Optional[int]
    createdAt: datetime
    updatedAt: datetime