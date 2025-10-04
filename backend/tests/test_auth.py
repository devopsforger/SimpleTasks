"""Test authentication endpoints and security utilities."""

import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import status

from app.auth.jwt import create_access_token, verify_token
from app.auth.security import verify_password, get_password_hash
from app.config import settings


class TestSecurityUtilities:
    """Test security utilities."""

    def test_password_hashing_and_verification(self):
        """Test password hashing and verification works correctly."""
        password = "Testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "Testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_verify_empty_password(self):
        """Test verification with empty password."""
        hashed = get_password_hash("password")
        assert verify_password("", hashed) is False

    def test_hash_empty_password(self):
        """Test hashing empty password."""
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True


class TestJWTUtilities:
    """Test JWT token functionality."""

    def test_create_access_token(self):
        """Test creating JWT access token with payload."""
        data = {"sub": "123", "role": "user"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """Test creating JWT token with custom expiry delta."""
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)

        assert token is not None

        # Verify expiry in payload
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert "exp" in payload
        assert "sub" in payload

    def test_create_access_token_without_expiry(self):
        """Test creating JWT token with default expiry."""
        data = {"sub": "123"}
        token = create_access_token(data)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert "exp" in payload

    def test_verify_valid_token(self):
        """Test verifying valid JWT token."""
        data = {"sub": "123", "custom": "data"}
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["custom"] == "data"

    def test_verify_invalid_token(self):
        """Test verifying invalid JWT token."""
        payload = verify_token("invalid_token_string")
        assert payload is None

    def test_verify_malformed_token(self):
        """Test verifying malformed JWT token."""
        payload = verify_token("header.payload.signature")
        assert payload is None

    def test_verify_expired_token(self):
        """Test verifying expired JWT token."""
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=-5)  # Expired
        token = create_access_token(data, expires_delta)
        payload = verify_token(token)

        assert payload is None

    def test_verify_token_wrong_secret(self):
        """Test verifying token with wrong secret key."""
        data = {"sub": "123"}
        token = create_access_token(data)

        # Try to decode with wrong secret
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong-secret", algorithms=[settings.JWT_ALGORITHM])


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "Newpassword123",
            "is_admin": False,
        }
        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] is not None
        assert data["is_admin"] is False
        assert isinstance(data["access_token"], str)

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,  # Already exists
            "password": "Password123",
            "is_admin": False,
        }
        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "password": "password123",
            "is_admin": False,
        }
        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client):
        """Test registration with weak password."""
        user_data = {
            "email": "user@example.com",
            "password": "123",  # Too short
            "is_admin": False,
        }
        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        user_data = {
            "email": "user@example.com",
            # Missing password
        }
        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        """Test successful login with correct credentials."""
        login_data = {
            "username": test_user.email,
            "password": "Testpassword123",
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == test_user.id
        assert data["is_admin"] is False

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password."""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword",
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent user email."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123",
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, test_db, test_user):
        """Test login with inactive user account."""
        # Deactivate user
        from app.services.user_service import UserService
        from app.schemas.user import UserUpdate

        update_data = UserUpdate(is_active=False)
        await UserService.update(test_db, test_user.id, update_data)

        login_data = {
            "username": test_user.email,
            "password": "Testpassword123",
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_login_admin_user(self, client, test_admin):
        """Test login with admin user credentials."""
        login_data = {
            "username": test_admin.email,
            "password": "Adminpassword123",
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_admin"] is True

    @pytest.mark.asyncio
    async def test_login_missing_credentials(self, client):
        """Test login with missing credentials."""
        login_data = {}  # Missing username and password
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_login_empty_password(self, client, test_user):
        """Test login with empty password."""
        login_data = {
            "username": test_user.email,
            "password": "",
        }
        response = await client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_token_authentication_flow(self, client):
        """Test complete authentication flow with token usage."""
        # Register new user
        user_data = {
            "email": "flow@example.com",
            "password": "Flowpassword123",
            "is_admin": False,
        }
        register_response = await client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK
        token = register_response.json()["access_token"]

        # Use token to access protected endpoint
        client.headers = {"Authorization": f"Bearer {token}"}
        profile_response = await client.get("/api/v1/users/me")

        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()
        assert profile_data["email"] == "flow@example.com"
