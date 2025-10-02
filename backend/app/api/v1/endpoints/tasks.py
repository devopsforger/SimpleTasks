"""
Task management API endpoints.

This module defines the task-related API routes including task CRUD operations
with proper authorization checks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from app.database import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services.task_service import TaskService
from app.api.deps import get_current_active_user, require_admin

# Router for task endpoints
router = APIRouter()


@router.get("/", response_model=List[Task])
async def get_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
):
    """
    Get tasks based on user role.

    Admins get all tasks, regular users get only their own tasks.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        db: Database session
        current_user: Authenticated user

    Returns:
        List[Task]: List of task objects
    """
    if current_user.is_admin:
        tasks = await TaskService.get_all(db, skip=skip, limit=limit)
    else:
        tasks = await TaskService.get_by_owner(
            db, current_user.id, skip=skip, limit=limit
        )
    return tasks


@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Create a new task.

    The task will be automatically assigned to the current user.

    Args:
        task: Task creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: Newly created task object
    """
    return await TaskService.create(db, task, current_user.id)


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Get specific task by ID.

    Users can only access their own tasks unless they are admins.

    Args:
        task_id: ID of task to retrieve
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: Task object

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 403 if user doesn't have permission to access task
    """
    task = await TaskService.get_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Check access permissions
    if not current_user.is_admin and task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Fully update a task.

    Users can only update their own tasks unless they are admins.

    Args:
        task_id: ID of task to update
        task_update: Task update data
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: Updated task object

    Raises:
        HTTPException: 403 if user doesn't have permission to update task
        HTTPException: 404 if task not found
    """
    # Check access permissions
    can_access = await TaskService.can_access_task(
        db, task_id, current_user.id, current_user.is_admin
    )
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Update task
    task = await TaskService.update(db, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task


@router.patch("/{task_id}", response_model=Task)
async def partial_update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Partially update a task.

    Users can only update their own tasks unless they are admins.

    Args:
        task_id: ID of task to update
        task_update: Partial task update data
        db: Database session
        current_user: Authenticated user

    Returns:
        Task: Updated task object

    Raises:
        HTTPException: 403 if user doesn't have permission to update task
        HTTPException: 404 if task not found
    """
    # Check access permissions
    can_access = await TaskService.can_access_task(
        db, task_id, current_user.id, current_user.is_admin
    )
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Update task
    task = await TaskService.update(db, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Delete a task.

    Users can only delete their own tasks unless they are admins.

    Args:
        task_id: ID of task to delete
        db: Database session
        current_user: Authenticated user

    Returns:
        dict: Success message

    Raises:
        HTTPException: 403 if user doesn't have permission to delete task
        HTTPException: 404 if task not found
    """
    # Check access permissions
    can_access = await TaskService.can_access_task(
        db, task_id, current_user.id, current_user.is_admin
    )
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Delete task
    success = await TaskService.delete(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return {"message": "Task deleted successfully"}
