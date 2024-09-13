from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database.config import Base
from .Task import task_executors_association
import enum


class UserRole(enum.IntEnum):
    ADMIN = 1
    DEVELOPER = 2
    USER = 3
    WATCHER = 4


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.WATCHER)
    tasks = relationship(
        "Task", secondary=task_executors_association, back_populates="executors"
    )
