"""
User Pydantic schemas for request/response validation.

This module defines all Pydantic models used for user-related API operations,
including data validation, serialization, and documentation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    """
    Base user schema with common attributes.

    Attributes:
        email (EmailStr): User's email address
        is_active (bool): Whether the user account is active
        is_admin (bool): Whether the user has admin privileges
    """

    email: EmailStr
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False


class UserCreate(UserBase):
    """
    Schema for user creation requests.

    Extends UserBase with password field for registration.

    Attributes:
        password (str): Plain text password for new user
    """

    password: str


class UserUpdate(BaseModel):
    """
    Schema for user update requests.

    All fields are optional to allow partial updates.

    Attributes:
        email (EmailStr): New email address
        is_active (bool): New active status
        is_admin (bool): New admin status
    """

    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class User(UserBase):
    """
    User response schema.

    Used for serializing user data in API responses.

    Attributes:
        id (int): User identifier
    """

    id: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserInDB(User):
    """
    Extended user schema including database-specific fields.

    Used internally, not exposed via API.

    Attributes:
        hashed_password (str): Hashed password stored in database
    """

    hashed_password: str
