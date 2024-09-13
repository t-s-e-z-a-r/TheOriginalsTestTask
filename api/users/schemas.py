from pydantic import BaseModel, EmailStr
from typing import Optional
from database.models import UserRole


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    role: UserRole
