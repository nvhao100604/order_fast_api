from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from app.models.enum import Status
from app.schemas.base import BaseSchema

class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=255)
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phoneNumber: str = Field(..., pattern=r"^\d{10}$")
    address: Optional[str] = Field(None, max_length=255)
    status: Status = Status.ACTIVE
    roleID: Optional[int] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)

class UserUpdate(BaseSchema):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None
    address: Optional[str] = None

class UserResponse(UserBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

class UserFilter(UserUpdate):
    pass