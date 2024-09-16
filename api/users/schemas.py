from pydantic import BaseModel, EmailStr
from typing import Optional
from database.models import UserRole


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.WATCHER


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    role: UserRole
