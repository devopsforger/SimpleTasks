"""
FastAPI dependencies for authentication and authorization.

This module provides dependency functions that can be used in route handlers
to handle JWT authentication, user retrieval, and role-based access control.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database import get_db
from app.auth.jwt import verify_token
from app.services.user_service import UserService

# HTTP Bearer security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify JWT token
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    # Extract user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Convert string to integer for database query
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    # Retrieve user from database
    user = await UserService.get_by_id(db, user_id_int)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Dependency to ensure current user is active.

    Args:
        current_user: User object from get_current_user dependency

    Returns:
        User: Active user object

    Raises:
        HTTPException: 400 if user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def require_admin(
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Dependency to require admin privileges.

    Args:
        current_user: Active user object from get_current_active_user dependency

    Returns:
        User: User object with admin privileges

    Raises:
        HTTPException: 403 if user doesn't have admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    return current_user
