"""
Task service layer for business logic and database operations.

This module contains the TaskService class that abstracts all database operations
related to tasks, including authorization checks and business logic.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service class for task-related database operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            db (AsyncSession): Database session
            task_id (int): Task identifier to search for

        Returns:
            Optional[Task]: Task object if found, None otherwise
        """
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Retrieve all tasks with pagination.

        Args:
            db (AsyncSession): Database session
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            List[Task]: List of task objects
        """
        result = await db.execute(select(Task).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_owner(
        db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """
        Retrieve tasks belonging to a specific user.

        Args:
            db (AsyncSession): Database session
            owner_id (int): User ID to filter tasks by
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            List[Task]: List of task objects owned by the specified user
        """
        result = await db.execute(
            select(Task).where(Task.owner_id == owner_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, task: TaskCreate, owner_id: int) -> Task:
        """
        Create a new task for a user.

        Args:
            db (AsyncSession): Database session
            task (TaskCreate): Task creation data
            owner_id (int): ID of user who owns this task

        Returns:
            Task: Newly created task object
        """
        db_task = Task(**task.dict(), owner_id=owner_id)
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task

    @staticmethod
    async def update(
        db: AsyncSession, task_id: int, task_update: TaskUpdate
    ) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            db (AsyncSession): Database session
            task_id (int): ID of task to update
            task_update (TaskUpdate): Update data

        Returns:
            Optional[Task]: Updated task object if found, None otherwise
        """
        db_task = await TaskService.get_by_id(db, task_id)
        if not db_task:
            return None

        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        await db.commit()
        await db.refresh(db_task)
        return db_task

    @staticmethod
    async def delete(db: AsyncSession, task_id: int) -> bool:
        """
        Delete a task from the database.

        Args:
            db (AsyncSession): Database session
            task_id (int): ID of task to delete

        Returns:
            bool: True if task was deleted, False if task not found
        """
        db_task = await TaskService.get_by_id(db, task_id)
        if not db_task:
            return False

        await db.delete(db_task)
        await db.commit()
        return True

    @staticmethod
    async def can_access_task(
        db: AsyncSession, task_id: int, user_id: int, is_admin: bool
    ) -> bool:
        """
        Check if a user can access a specific task.

        Admins can access all tasks, regular users can only access their own tasks.

        Args:
            db (AsyncSession): Database session
            task_id (int): ID of task to check access for
            user_id (int): ID of user requesting access
            is_admin (bool): Whether the user has admin privileges

        Returns:
            bool: True if user can access the task, False otherwise
        """
        if is_admin:
            return True

        task = await TaskService.get_by_id(db, task_id)
        return task and task.owner_id == user_id
