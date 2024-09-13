from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.config import get_async_session
from database.models import Task

from .schemas import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskSchema

task_router = APIRouter()


@task_router.get("/", response_model=List[TaskSchema])
async def get_tasks(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return tasks


@task_router.post("/", response_model=TaskSchema)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_async_session)):
    new_task = Task(**task.dict())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


@task_router.patch("/{task_id}", response_model=TaskSchema)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(select(Task).filter_by(id=task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    task.status = status_update.status
    await db.commit()
    await db.refresh(task)
    return task


@task_router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(Task).filter_by(id=task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


@task_router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task).filter_by(id=task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully"}
