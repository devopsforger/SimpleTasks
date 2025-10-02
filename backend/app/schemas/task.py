"""
Task Pydantic schemas for request/response validation.

This module defines all Pydantic models used for task-related API operations,
including data validation, serialization, and documentation.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.task import TaskStatus
from app.schemas.user import User


class TaskBase(BaseModel):
    """
    Base task schema with common attributes.

    Attributes:
        title (str): Task title
        description (str): Detailed task description
        status (TaskStatus): Current task status
    """

    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO


class TaskCreate(TaskBase):
    """
    Schema for task creation requests.

    Inherits all fields from TaskBase.
    """


class TaskUpdate(BaseModel):
    """
    Schema for task update requests.

    All fields are optional to allow partial updates.

    Attributes:
        title (str): New task title
        description (str): New task description
        status (TaskStatus): New task status
    """

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class Task(TaskBase):
    """
    Task response schema.

    Used for serializing task data in API responses, includes relationship data.

    Attributes:
        id (int): Task identifier
        owner_id (int): ID of the user who owns this task
        created_at (datetime): When the task was created
        owner (User): User object representing the task owner
    """

    id: int
    owner_id: int
    created_at: datetime
    owner: User

    class Config:
        """Pydantic configuration."""

        from_attributes = True
