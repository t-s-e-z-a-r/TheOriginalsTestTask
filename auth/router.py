from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models import User
from database.config import get_async_session

from .schemas import Token, UserLogin

from tools import hash_password, create_token, verify_password

auth_router = APIRouter()


@auth_router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_async_session)):
    async with db as session:
        result = await session.execute(
            select(User).where(User.username == user_data.username)
        )
        user = result.scalars().first()

        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        access_token = create_token(user)
        return Token(access_token=access_token, token_type="bearer")
