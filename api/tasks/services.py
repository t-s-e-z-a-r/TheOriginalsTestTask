from fastapi import HTTPException, status

from sqlalchemy import insert
from sqlalchemy.future import select

from database.models import User, task_executors_association


async def add_executors(db, task_id, executors):
    result = await db.execute(select(User).where(User.id.in_(executors)))
    users = result.scalars().all()

    if len(users) != len(executors):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="One or more users not found"
        )

    for user_id in executors:
        stmt = insert(task_executors_association).values(
            task_id=task_id, user_id=user_id
        )
        await db.execute(stmt)

    return users
