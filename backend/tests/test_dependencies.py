"""Test FastAPI dependencies and middleware."""

import pytest
from fastapi import status, HTTPException
from unittest.mock import AsyncMock, patch

from app.api.deps import get_current_user, get_current_active_user, require_admin
from app.services.user_service import UserService


class TestDependencies:
    """Test API dependencies."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, test_db, test_user):
        """Test successful current user retrieval."""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = "valid_token"

        with patch("app.api.deps.verify_token") as mock_verify:
            mock_verify.return_value = {"sub": str(test_user.id)}

            with patch("app.api.deps.UserService.get_by_id") as mock_get_user:
                mock_get_user.return_value = test_user

                user = await get_current_user(mock_credentials, test_db)
                assert user == test_user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, test_db):
        """Test current user retrieval with invalid token."""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = "invalid_token"

        with patch("app.api.deps.verify_token") as mock_verify:
            mock_verify.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, test_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub(self, test_db):
        """Test current user retrieval with token missing sub claim."""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = "token_without_sub"

        with patch("app.api.deps.verify_token") as mock_verify:
            mock_verify.return_value = {"other_claim": "value"}  # No 'sub'

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, test_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, test_db):
        """Test current user retrieval when user doesn't exist."""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = "valid_token"

        with patch("app.api.deps.verify_token") as mock_verify:
            mock_verify.return_value = {"sub": "999"}  # Non-existent user

            with patch("app.api.deps.UserService.get_by_id") as mock_get_user:
                mock_get_user.return_value = None

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_credentials, test_db)

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_active_user_success(self, test_user):
        """Test successful active user retrieval."""
        user = await get_current_active_user(test_user)
        assert user == test_user

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self, test_db, test_user):
        """Test active user retrieval with inactive user."""
        test_user.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(test_user)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "inactive" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_require_admin_success(self, test_admin):
        """Test successful admin requirement check."""
        user = await require_admin(test_admin)
        assert user == test_admin

    @pytest.mark.asyncio
    async def test_require_admin_non_admin(self, test_user):
        """Test admin requirement check with non-admin user."""
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(test_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "permissions" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_dependency_chain(self, test_db, test_admin):
        """Test dependency chain: active user -> admin."""
        # This tests that the dependencies can be chained together
        active_user = await get_current_active_user(test_admin)
        admin_user = await require_admin(active_user)
        assert admin_user == test_admin

    @pytest.mark.asyncio
    async def test_invalid_user_id_format(self, test_db):
        """Test current user retrieval with invalid user ID format in token."""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = "valid_token"

        with patch("app.api.deps.verify_token") as mock_verify:
            mock_verify.return_value = {"sub": "not_an_integer"}  # Invalid ID format

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, test_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
