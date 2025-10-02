"""
FastAPI application entry point.

This module creates and configures the FastAPI application instance,
sets up middleware, and includes all API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

# Create FastAPI application instance
app = FastAPI(
    title="Task Management API",
    description="Backend API for Task Management Application with JWT authentication and role-based access control",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Service status information
    """
    return {"status": "ok", "service": "backend"}


@app.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        dict: Welcome message
    """
    return {"message": "Task Management API"}
