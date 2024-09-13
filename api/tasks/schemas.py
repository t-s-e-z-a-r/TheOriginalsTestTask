from pydantic import BaseModel
from typing import List, Optional


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskSchema(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    assignee: Optional[int] = None
    status: str


class TaskStatusUpdate(BaseModel):
    status: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    assignee: Optional[int] = None


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: Optional[int] = None
    assignee: Optional[int] = None
