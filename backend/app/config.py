"""
Application configuration settings module.

This module defines the configuration settings for the Task Management API
using Pydantic settings management. It handles environment variables,
default values, and computed properties like database URLs.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings configuration.

    This class defines all configuration parameters needed by the application,
    with support for environment variable loading and default values.

    Attributes:
        DB_HOST (str): Database host address
        DB_PORT (str): Database port number
        DB_NAME (str): Database name
        DB_USER (str): Database username
        DB_PASSWORD (str): Database password
        JWT_SECRET_KEY (str): Secret key for JWT token encoding/decoding
        JWT_ALGORITHM (str): Algorithm used for JWT tokens
        ACCESS_TOKEN_EXPIRE_MINUTES (int): JWT token expiration time in minutes
        DEBUG (bool): Application debug mode flag
    """

    # Database configuration
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "taskmanager"
    DB_USER: str = "postgres"
    DB_PASSWORD: str

    # JWT configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application configuration
    DEBUG: bool = False

    @property
    def DATABASE_URL(self) -> str:
        """
        Construct and return the async PostgreSQL database URL.

        Returns:
            str: Fully formatted database URL for asyncpg driver
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        """Pydantic configuration class."""

        env_file = ".env"


# Global settings instance
settings = Settings()
