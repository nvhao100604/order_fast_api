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

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)
    # Các trường tùy chọn tùy theo Role
    roleID: Optional[int] = None 

class UserUpdate(BaseSchema):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None
    address: Optional[str] = None
    status: Optional[Status] = None

class UserResponse(UserBase):
    id: int
    roleID: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

class UserFilter(UserUpdate):
    pass