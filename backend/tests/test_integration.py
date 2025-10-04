"""Test integration scenarios and end-to-end workflows."""

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.task import TaskStatus


class TestIntegrationWorkflows:
    """Test integration workflows."""

    @pytest.mark.asyncio
    async def test_full_user_workflow(self, client, test_db):
        """Test complete user registration and task management workflow."""
        # 1. Register new user
        user_data = {
            "email": "workflow@example.com",
            "password": "Workflowpassword123",
            "is_admin": False,
        }
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        user_id = response.json()["user_id"]

        profile_response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.json()["email"] == "workflow@example.com"

        # 4. Create multiple tasks
        tasks_data = [
            {"title": "Workflow Task 1", "status": TaskStatus.TODO},
            {
                "title": "Workflow Task 2",
                "description": "Second task",
                "status": TaskStatus.IN_PROGRESS,
            },
            {"title": "Workflow Task 3", "status": TaskStatus.DONE},
        ]

        created_tasks = []
        for task_data in tasks_data:
            response = await client.post(
                "/api/v1/tasks/",
                headers={"Authorization": f"Bearer {token}"},
                json=task_data,
            )
            assert response.status_code == status.HTTP_200_OK
            created_tasks.append(response.json())

        # 5. Get all tasks
        response = await client.get(
            "/api/v1/tasks/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()
        assert len(tasks) == 3

        # 6. Update a task
        task_id = created_tasks[0]["id"]
        update_data = {"status": TaskStatus.IN_PROGRESS}
        response = await client.patch(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == TaskStatus.IN_PROGRESS

        # 7. Delete a task
        response = await client.delete(
            f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK

        # 8. Verify task is deleted
        response = await client.get(
            "/api/v1/tasks/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_admin_user_management_workflow(
        self, admin_client, test_db, test_user
    ):
        """Test admin user management workflow."""
        # 1. Get all users
        response = await admin_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_200_OK
        initial_users = response.json()
        initial_count = len(initial_users)

        # 2. Promote regular user to admin
        update_data = {"is_admin": True}
        response = await admin_client.patch(
            f"/api/v1/users/{test_user.id}", json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_admin"] is True

        # 3. Verify user is now admin
        response = await admin_client.get(f"/api/v1/users/{test_user.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_admin"] is True

        # 4. Deactivate user
        update_data = {"is_active": False}
        response = await admin_client.patch(
            f"/api/v1/users/{test_user.id}", json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_active"] is False

        # 5. Delete user
        response = await admin_client.delete(f"/api/v1/users/{test_user.id}")
        assert response.status_code == status.HTTP_200_OK

        # 6. Verify user is deleted
        response = await admin_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == initial_count - 1

    @pytest.mark.asyncio
    async def test_multi_user_task_isolation(
        self, client, test_db, test_user, another_user
    ):
        """Test that users can only see their own tasks."""
        # Login as first user
        login_data1 = {"username": test_user.email, "password": "Testpassword123"}
        response1 = await client.post("/api/v1/auth/login", data=login_data1)
        assert response1.status_code == status.HTTP_200_OK
        token1 = response1.json()["access_token"]

        # Create task as first user
        task_data = {"title": "First User Task"}
        response = await client.post(
            "/api/v1/tasks/",
            headers={"Authorization": f"Bearer {token1}"},
            json=task_data,
        )

        assert response.status_code == status.HTTP_200_OK
        first_user_task_id = response.json()["id"]

        # Login as second user
        login_data2 = {"username": another_user.email, "password": "Anotherpassword123"}
        response2 = await client.post("/api/v1/auth/login", data=login_data2)
        assert response2.status_code == status.HTTP_200_OK
        token2 = response2.json()["access_token"]

        # Create task as second user
        task_data = {"title": "Second User Task"}
        response = await client.post(
            "/api/v1/tasks/",
            headers={"Authorization": f"Bearer {token2}"},
            json=task_data,
        )
        assert response.status_code == status.HTTP_200_OK
        second_user_task_id = response.json()["id"]

        # Second user should only see their own task
        response = await client.get(
            "/api/v1/tasks/",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Second User Task"
        assert tasks[0]["id"] == second_user_task_id

        # Second user should not be able to access first user's task
        response = await client.get(
            f"/api/v1/tasks/{first_user_task_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_access_all_data(
        self, admin_client, test_user, another_user, test_task
    ):
        """Test admin can access all users and tasks."""
        # Admin can see all users
        response = await admin_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        user_emails = [user["email"] for user in users]
        assert test_user.email in user_emails
        assert another_user.email in user_emails

        # Admin can see all tasks
        response = await admin_client.get("/api/v1/tasks/")
        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()
        assert len(tasks) >= 1

        # Admin can access any user's task
        response = await admin_client.get(f"/api/v1/tasks/{test_task.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == test_task.id

    @pytest.mark.asyncio
    async def test_token_authentication_flow(self, client):
        """Test complete token-based authentication flow."""
        # Register new user
        user_data = {
            "email": "tokenflow@example.com",
            "password": "Tokenflow123",
            "is_admin": False,
        }
        register_response = await client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK
        register_token = register_response.json()["access_token"]

        profile_response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {register_token}"}
        )
        assert profile_response.status_code == status.HTTP_200_OK

        # Login to get new token
        login_data = {
            "username": "tokenflow@example.com",
            "password": "Tokenflow123",
        }
        login_response = await client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        login_token = login_response.json()["access_token"]

        # Use login token
        profile_response2 = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert profile_response2.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_base_client_is_unauthenticated(self, client):
        """Verify that the base client fixture has no authentication headers."""
        # Check that client has no auth headers
        if hasattr(client, "headers"):
            auth_header = client.headers.get("Authorization")
            assert auth_header is None, (
                f"Base client should have no auth headers, but has: {auth_header}"
            )

        # Test multiple endpoints that should return 401
        endpoints = ["/api/v1/users/me", "/api/v1/tasks/", "/api/v1/users/"]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
                f"Endpoint {endpoint} should return 401 for unauthenticated requests, but got {response.status_code}"
            )

    @pytest.mark.asyncio
    async def test_error_handling_flow(
        self, unauthenticated_client, auth_client, admin_client
    ):
        """Test error handling in various scenarios."""
        # Access protected endpoint without token - should be 401 Unauthorized
        response = await unauthenticated_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Access admin endpoint as regular user - should be 403 Forbidden
        response = await auth_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Access non-existent resource - should be 404 Not Found
        response = await admin_client.get("/api/v1/users/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Create task with invalid data - should be 422 Unprocessable Entity
        response = await auth_client.post("/api/v1/tasks/", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Update user with invalid data - should be 422 Unprocessable Entity
        # First get a valid user ID
        users_response = await admin_client.get("/api/v1/users/")
        assert users_response.status_code == status.HTTP_200_OK
        users = users_response.json()
        if users:
            user_id = users[0]["id"]
            response = await admin_client.patch(
                f"/api/v1/users/{user_id}", json={"email": "invalid-email"}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestHealthCheck:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint returns correct response."""
        response = await client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "backend"

    @pytest.mark.asyncio
    async def test_health_check_multiple_requests(self, client):
        """Test health check endpoint handles multiple requests."""
        for i in range(5):
            response = await client.get("/health")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "ok"
