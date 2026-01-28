from pydantic import EmailStr
from typing import Optional, List
from .base import BaseSchema

class RoleBase(BaseSchema):
    name: str

class RoleResponse(RoleBase):
    id: int

class StaffBase(BaseSchema):
    name: str
    email: EmailStr
    phoneNumber: str
    username: str
    roleID: int
    status: int = 1

class StaffCreate(StaffBase):
    password: str 

class StaffResponse(StaffBase):
    id: int
