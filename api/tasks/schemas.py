from pydantic import BaseModel
from typing import List, Optional

from database.models import PriorityEnum, StatusEnum
from api.users.schemas import UserResponse


class TaskSchema(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    priority: PriorityEnum
    assignee_id: Optional[int] = None
    status: str
    executors: Optional[List[UserResponse]] = []


class TaskStatusUpdate(BaseModel):
    status: StatusEnum


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    assignee_id: Optional[int] = None


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: Optional[PriorityEnum] = None
    assignee_id: Optional[int] = None


class TaskExecutorsCreate(BaseModel):
    user_ids: List[int]
