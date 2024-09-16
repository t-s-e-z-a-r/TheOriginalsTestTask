from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from database.config import get_async_session
from database.models import User
from .schemas import UserCreate, UserResponse, UserUpdate
from tools import hash_password
from typing import List

user_router = APIRouter()


@user_router.post("/", response_model=UserResponse)
async def register(
    user_data: UserCreate, db: AsyncSession = Depends(get_async_session)
):
    async with db as session:
        result = await session.execute(
            select(User).where(
                or_(User.username == user_data.username, User.email == user_data.email)
            )
        )
        user = result.scalars().first()

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user


@user_router.get("/", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_async_session)):
    async with db as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
    return users


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_session)):
    async with db as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_async_session)
):
    async with db as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.role = user_update.role

        await session.commit()
        await session.refresh(user)
        return user


@user_router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_session)):
    async with db as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}
