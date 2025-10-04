"""
Authentication API endpoints.

This module defines the authentication-related API routes including
user registration and login.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession


from app.database import get_db
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.auth.jwt import create_access_token
from app.config import settings

# Router for authentication endpoints
router = APIRouter()


@router.post("/register")
async def register(user_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Register a new user account.

    Args:
        user_data: User registration data including email and password
        db: Database session

    Returns:
        dict: Access token and user information

    Raises:
        HTTPException: 400 if email is already registered
    """
    # Check if user already exists
    existing_user = await UserService.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    user = await UserService.create(db, user_data)

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "is_admin": user.is_admin,
    }


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Authenticate user and return JWT token.

    Args:
        form_data: OAuth2 password form data (username=email, password)
        db: Database session

    Returns:
        dict: Access token and user information

    Raises:
        HTTPException: 401 if authentication fails
    """
    # Authenticate user
    user = await UserService.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "is_admin": user.is_admin,
    }
