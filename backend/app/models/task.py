"""
Task model definition.

This module defines the Task SQLAlchemy model representing user tasks
with status tracking and ownership.
"""

import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class TaskStatus(str, enum.Enum):
    """
    Enumeration representing possible task statuses.

    Attributes:
        TODO: Task has been created but not started
        IN_PROGRESS: Task is currently being worked on
        DONE: Task has been completed
    """

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    """
    Task model representing user tasks.

    Attributes:
        id (int): Primary key identifier
        title (str): Task title
        description (str): Detailed task description
        status (TaskStatus): Current status of the task
        created_at (DateTime): Timestamp when task was created
        owner_id (int): Foreign key to the user who owns this task
        owner (Relationship): Many-to-one relationship with User model
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship with owner (many tasks belong to one user)
    owner = relationship("User", back_populates="tasks", lazy="selectin")

    def __init__(self, **kwargs):
        # Set defaults if not provided
        kwargs.setdefault("status", TaskStatus.TODO)
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title})>"
