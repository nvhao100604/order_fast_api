from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, AliasChoices, field_validator
from typing import Optional, Union
from app.models.enum import Status
from app.schemas.base import BaseSchema

class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=255)
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phoneNumber: str = Field(..., pattern=r"^\d{10}$")
    address: Optional[str] = Field(None, max_length=255)
    status: Union[Status, str] = Status.ACTIVE
    roleID: Optional[int] = Field(None, validation_alias=AliasChoices('roleID', 'roleId'))

    @field_validator('status', mode='before')
    @classmethod
    def parse_status(cls, v):
        if isinstance(v, str):
            val_upper = v.upper()
            if val_upper in Status.__members__:
                return Status[val_upper]
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)

class UserUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = Field(None, pattern=r"^\d{10}$")
    address: Optional[str] = Field(None, max_length=255)

class UserAdminUpdate(UserUpdate):
    status: Optional[Union[Status, str]] = None
    roleID: Optional[int] = Field(None, validation_alias=AliasChoices('roleID', 'roleId'))

    @field_validator('status', mode='before')
    @classmethod
    def parse_status(cls, v):
        if isinstance(v, str):
            val_upper = v.upper()
            if val_upper in Status.__members__:
                return Status[val_upper]
        return v

class UserResponse(UserBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

class UserFilter(BaseSchema):
    search: Optional[str] = None
    roleID: Optional[int] = Field(None, validation_alias=AliasChoices('roleID', 'roleId'))
    status: Optional[Union[Status, str]] = None

    @field_validator('status', mode='before')
    @classmethod
    def parse_status(cls, v):
        if isinstance(v, str):
            val_upper = v.upper()
            if val_upper in Status.__members__:
                return Status[val_upper]
        return v


class SendOTPRequest(BaseSchema):
    email: EmailStr

class VerifyOTPRequest(BaseSchema):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class ResetPasswordRequest(BaseSchema):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    newPassword: str = Field(..., min_length=6, max_length=72)