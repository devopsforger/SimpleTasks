"""
User model definition.

This module defines the User SQLAlchemy model representing application users
with authentication and authorization capabilities.
"""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """
    User model representing application users.

    Attributes:
        id (int): Primary key identifier
        email (str): Unique email address used for authentication
        hashed_password (str): BCrypt hashed password
        is_active (bool): Flag indicating if user account is active
        is_admin (bool): Flag indicating if user has admin privileges
        tasks (Relationship): One-to-many relationship with Task model
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationship with tasks (one user can have many tasks)
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
