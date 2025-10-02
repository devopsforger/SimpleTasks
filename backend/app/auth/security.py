"""
Password hashing and verification utilities.

This module provides functions for securely hashing passwords
and verifying them against stored hashes using bcrypt.
"""

from passlib.context import CryptContext

# Configure password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): BCrypt hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise

    Example:
        ```python
        is_valid = verify_password("mypassword", "$2b$12$...")
        ```
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Args:
        password (str): Plain text password to hash

    Returns:
        str: BCrypt hashed password

    Example:
        ```python
        hashed = get_password_hash("mypassword")
        ```
    """
    return pwd_context.hash(password)
