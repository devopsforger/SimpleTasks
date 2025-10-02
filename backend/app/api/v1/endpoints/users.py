"""
User management API endpoints.

This module defines the user-related API routes including user CRUD operations
and profile management. Most endpoints require admin privileges.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from app.database import get_db
from app.schemas.user import User, UserUpdate
from app.services.user_service import UserService
from app.api.deps import get_current_active_user, require_admin

# Router for user endpoints
router = APIRouter()


@router.get("/", response_model=List[User])
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_admin)],
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all users (admin only).

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        db: Database session
        current_user: Authenticated admin user

    Returns:
        List[User]: List of user objects
    """
    users = await UserService.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=User)
async def get_current_user(
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Get current user's profile.

    Args:
        current_user: Authenticated user

    Returns:
        User: Current user's profile data
    """
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_admin)],
):
    """
    Get specific user by ID (admin only).

    Args:
        user_id: ID of user to retrieve
        db: Database session
        current_user: Authenticated admin user

    Returns:
        User: User object

    Raises:
        HTTPException: 404 if user not found
    """
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_admin)],
):
    """
    Update user information (admin only).

    Args:
        user_id: ID of user to update
        user_update: User update data
        db: Database session
        current_user: Authenticated admin user

    Returns:
        User: Updated user object

    Raises:
        HTTPException: 404 if user not found
    """
    user = await UserService.update(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(require_admin)],
):
    """
    Delete user (admin only).

    Args:
        user_id: ID of user to delete
        db: Database session
        current_user: Authenticated admin user

    Returns:
        dict: Success message

    Raises:
        HTTPException: 400 if trying to delete own account
        HTTPException: 404 if user not found
    """
    # Prevent users from deleting their own account
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
        )

    # Delete user
    success = await UserService.delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"message": "User deleted successfully"}
