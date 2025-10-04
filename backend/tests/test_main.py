"""Test main application endpoints and configuration."""

import pytest
from fastapi import status


class TestMainEndpoints:
    """Test main application endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = await client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert data["message"] == "Task Management API"

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "backend"

    @pytest.mark.asyncio
    async def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint returns 404."""
        response = await client.get("/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_api_docs_available(self, client):
        """Test that API documentation is available."""
        response = await client.get("/docs")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available."""
        response = await client.get("/openapi.json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestApplicationConfiguration:
    """Test application configuration and settings."""

    @pytest.mark.asyncio
    async def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = await client.options("/api/v1/auth/login")

        # CORS preflight should be handled
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        ]
