"""
User service layer for business logic and database operations.

This module contains the UserService class that abstracts all database operations
related to users, providing a clean interface for the API layer.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.auth.security import get_password_hash, verify_password


class UserService:
    """Service class for user-related database operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            db (AsyncSession): Database session
            user_id (int): User identifier to search for

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            db (AsyncSession): Database session
            email (str): Email address to search for

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Retrieve all users with pagination.

        Args:
            db (AsyncSession): Database session
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            List[User]: List of user objects
        """
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, user: UserCreate) -> User:
        """
        Create a new user in the database.

        Args:
            db (AsyncSession): Database session
            user (UserCreate): User creation data

        Returns:
            User: Newly created user object

        Raises:
            ValueError: If user creation fails
        """
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            is_active=user.is_active,
            is_admin=user.is_admin,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def update(
        db: AsyncSession, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        """
        Update an existing user.

        Args:
            db (AsyncSession): Database session
            user_id (int): ID of user to update
            user_update (UserUpdate): Update data

        Returns:
            Optional[User]: Updated user object if found, None otherwise
        """
        db_user = await UserService.get_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """
        Delete a user from the database.

        Args:
            db (AsyncSession): Database session
            user_id (int): ID of user to delete

        Returns:
            bool: True if user was deleted, False if user not found
        """
        db_user = await UserService.get_by_id(db, user_id)
        if not db_user:
            return False

        await db.delete(db_user)
        await db.commit()
        return True

    @staticmethod
    async def authenticate(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            db (AsyncSession): Database session
            email (str): User's email address
            password (str): Plain text password

        Returns:
            Optional[User]: User object if authentication successful, None otherwise
        """
        user = await UserService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
