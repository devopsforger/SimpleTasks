"""
Task Pydantic schemas for request/response validation.

This module defines all Pydantic models used for task-related API operations,
including data validation, serialization, and documentation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

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

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title must be between 1 and 200 characters",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Task description cannot exceed 1000 characters",
    )
    status: Optional[TaskStatus] = TaskStatus.TODO

    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    """
    Schema for task creation requests.

    Inherits all fields from TaskBase.
    """

    pass


class TaskUpdate(BaseModel):
    """
    Schema for task update requests.

    All fields are optional to allow partial updates.

    Attributes:
        title (str): New task title
        description (str): New task description
        status (TaskStatus): New task status
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Task title must be between 1 and 200 characters",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Task description cannot exceed 1000 characters",
    )
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
    owner: User  # Make sure this is included

    class Config:
        """Pydantic configuration."""

        from_attributes = True
