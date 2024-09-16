from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from database.config import Base
import enum

task_executors_association = Table(
    "task_executors",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class StatusEnum(enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "In progress"
    DONE = "Done"


class PriorityEnum(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String)
    assignee_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.TODO)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.LOW)
    assignee = relationship("User", foreign_keys=[assignee_id])
    executors = relationship(
        "User", secondary=task_executors_association, back_populates="tasks"
    )
