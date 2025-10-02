"""
Database configuration and connection management.

This module sets up the SQLAlchemy async engine, session factory, and base class
for declarative models. It provides the database connection dependency for FastAPI.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

# Create async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
)

# Async session factory
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class for declarative models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Database dependency for FastAPI.

    Yields an async database session and ensures proper cleanup after request completion.

    Yields:
        AsyncSession: Async database session

    Example:
        ```python
        async def some_endpoint(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
