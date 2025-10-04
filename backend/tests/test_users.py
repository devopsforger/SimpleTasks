"""Test user management endpoints."""

import pytest
from fastapi import status


class TestUserEndpoints:
    """Test user management endpoints."""

    @pytest.mark.asyncio
    async def test_get_users_unauthorized(self, client):
        """Test getting users without authentication."""
        response = await client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_users_non_admin(self, auth_client):
        """Test getting users as non-admin user."""
        response = await auth_client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data
        assert "permissions" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_users_admin(self, admin_client, test_user, test_admin):
        """Test getting users as admin user."""
        response = await admin_client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # test_user + test_admin

        # Check that both users are in the response
        emails = [user["email"] for user in data]
        assert test_user.email in emails
        assert test_admin.email in emails

    @pytest.mark.asyncio
    async def test_get_users_pagination(self, admin_client, multiple_tasks):
        """Test getting users with pagination parameters."""
        response = await admin_client.get("/api/v1/users/?skip=1&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

    @pytest.mark.asyncio
    async def test_get_current_user(self, auth_client, test_user):
        """Test getting current user profile."""
        response = await auth_client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
        assert data["is_active"] is True
        assert data["is_admin"] is False

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_admin(self, admin_client, test_admin):
        """Test getting current user as admin."""
        response = await admin_client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_admin.email
        assert data["is_admin"] is True

    @pytest.mark.asyncio
    async def test_get_user_by_id_admin(self, admin_client, test_user):
        """Test getting specific user by ID as admin."""
        response = await admin_client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
        assert data["is_active"] == test_user.is_active
        assert data["is_admin"] == test_user.is_admin

    @pytest.mark.asyncio
    async def test_get_user_by_id_non_admin(self, auth_client, test_user):
        """Test getting specific user by ID as non-admin."""
        response = await auth_client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, admin_client):
        """Test getting non-existent user by ID."""
        response = await admin_client.get("/api/v1/users/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_user_by_id_invalid_id(self, admin_client):
        """Test getting user with invalid ID format."""
        response = await admin_client.get("/api/v1/users/invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_update_user_admin(self, admin_client, test_user):
        """Test updating user as admin."""
        update_data = {
            "is_admin": True,
            "is_active": False,
            "email": "updated@example.com",
        }
        response = await admin_client.patch(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_admin"] is True
        assert data["is_active"] is False
        assert data["email"] == "updated@example.com"

    @pytest.mark.asyncio
    async def test_update_user_partial_data(self, admin_client, test_user):
        """Test updating user with partial data."""
        update_data = {"is_admin": True}
        response = await admin_client.patch(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_admin"] is True
        assert data["email"] == test_user.email  # Unchanged
        assert data["is_active"] == test_user.is_active  # Unchanged

    @pytest.mark.asyncio
    async def test_update_user_non_admin(self, auth_client, test_user):
        """Test updating user as non-admin."""
        update_data = {"is_admin": True}
        response = await auth_client.patch(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, admin_client):
        """Test updating non-existent user."""
        update_data = {"is_admin": True}
        response = await admin_client.patch("/api/v1/users/9999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_user_invalid_email(self, admin_client, test_user):
        """Test updating user with invalid email."""
        update_data = {"email": "invalid-email"}
        response = await admin_client.patch(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email(
        self, admin_client, test_user, test_admin
    ):
        """Test updating user with duplicate email."""
        update_data = {"email": test_admin.email}  # Already exists
        response = await admin_client.patch(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_delete_user_admin(self, admin_client, test_user):
        """Test deleting user as admin."""
        response = await admin_client.delete(f"/api/v1/users/{test_user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()

        # Verify user is actually deleted
        get_response = await admin_client.get(f"/api/v1/users/{test_user.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_user_non_admin(self, auth_client, test_user):
        """Test deleting user as non-admin."""
        response = await auth_client.delete(f"/api/v1/users/{test_user.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_user_self(self, admin_client, test_admin):
        """Test admin trying to delete themselves."""
        response = await admin_client.delete(f"/api/v1/users/{test_admin.id}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "yourself" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, admin_client):
        """Test deleting non-existent user."""
        response = await admin_client.delete("/api/v1/users/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_user_with_tasks(self, admin_client, test_user, test_task):
        """Test deleting user who has tasks (should cascade delete)."""
        response = await admin_client.delete(f"/api/v1/users/{test_user.id}")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_user_lifecycle(self, admin_client):
        """Test complete user lifecycle: create → update → delete."""
        # Create user via registration
        user_data = {
            "email": "lifecycle@example.com",
            "password": "Lifecycle123",
            "is_admin": False,
        }
        register_response = await admin_client.post(
            "/api/v1/auth/register", json=user_data
        )
        assert register_response.status_code == status.HTTP_200_OK
        user_id = register_response.json()["user_id"]

        # Update user
        update_data = {"is_active": False}
        update_response = await admin_client.patch(
            f"/api/v1/users/{user_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["is_active"] is False

        # Delete user
        delete_response = await admin_client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == status.HTTP_200_OK
