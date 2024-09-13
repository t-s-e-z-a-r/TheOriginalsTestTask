from fastapi import APIRouter

from .tasks import task_router
from .users import user_router

api_router = APIRouter()
api_router.include_router(task_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])
