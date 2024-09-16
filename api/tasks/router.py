from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.config import get_async_session
from database.models import Task, User

from .schemas import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskSchema,
    TaskExecutorsCreate,
)
from .services import add_executors

from api.users.schemas import UserResponse
from celery_app import send_status_change_email

task_router = APIRouter()


@task_router.get("/", response_model=List[TaskSchema])
async def get_tasks(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task).options(selectinload(Task.executors)))
    tasks = result.scalars().all()
    return tasks


@task_router.get("/{task_id}", response_model=TaskSchema)
async def get_tasks(task_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(Task).where(Task.id == task_id).options(selectinload(Task.executors))
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@task_router.post("/", response_model=TaskSchema)
async def create_task(
    request: Request, task: TaskCreate, db: AsyncSession = Depends(get_async_session)
):
    if task.assignee_id == None:
        task.assignee_id = request.state.user
    else:
        result = await db.execute(select(User).filter_by(id=task.assignee_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignee user not found"
            )
    new_task = Task(**task.dict())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task, attribute_names=["executors"])
    return new_task


@task_router.patch("/{task_id}", response_model=TaskSchema)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(Task)
        .filter_by(id=task_id)
        .options(selectinload(Task.assignee), selectinload(Task.executors))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    task.status = status_update.status
    await db.commit()
    send_status_change_email.apply_async((task.id, task.title, task.status.name, task.assignee.email))
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

    if task_update.assignee_id is not None:
        result = await db.execute(select(User).filter_by(id=task_update.assignee_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignee user not found"
            )

    update_data = task_update.dict(exclude_unset=True, exclude={"executors"})
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task, attribute_names=["executors"])
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


@task_router.post("/{task_id}/executors", response_model=List[UserResponse])
async def add_executor(
    task_id: int,
    data: TaskExecutorsCreate,
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(select(Task).filter_by(id=task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    executors = await add_executors(db, task.id, data.user_ids)
    await db.commit()
    return executors
