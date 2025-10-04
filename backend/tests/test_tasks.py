"""Test task management endpoints."""

import pytest
from fastapi import status
from app.models.task import TaskStatus


class TestTaskEndpoints:
    """Test task management endpoints."""

    @pytest.mark.asyncio
    async def test_get_tasks_unauthorized(self, client):
        """Test getting tasks without authentication."""
        response = await client.get("/api/v1/tasks/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_tasks_user(self, auth_client, test_task):
        """Test getting tasks as regular user."""
        response = await auth_client.get("/api/v1/tasks/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == test_task.title
        assert data[0]["owner_id"] == test_task.owner_id
        assert data[0]["status"] == test_task.status.value

    @pytest.mark.asyncio
    async def test_get_tasks_admin(self, admin_client, test_task, another_user):
        """Test getting all tasks as admin."""
        response = await admin_client.get("/api/v1/tasks/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_tasks_pagination(self, auth_client, multiple_tasks):
        """Test getting tasks with pagination."""
        response = await auth_client.get("/api/v1/tasks/?skip=1&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_pagination(self, auth_client):
        """Test getting tasks with invalid pagination parameters."""
        response = await auth_client.get("/api/v1/tasks/?skip=-1&limit=0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_task_success(self, auth_client, test_user):
        """Test creating a new task successfully."""
        task_data = {
            "title": "New Task",
            "description": "New Description",
            "status": TaskStatus.TODO,
        }
        response = await auth_client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "New Description"
        assert data["status"] == TaskStatus.TODO
        assert data["owner_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data
        assert "owner" in data

    @pytest.mark.asyncio
    async def test_create_task_minimal_data(self, auth_client, test_user):
        """Test creating task with minimal required data."""
        task_data = {"title": "Minimal Task"}
        response = await auth_client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["status"] == TaskStatus.TODO
        assert data["owner_id"] == test_user.id

    @pytest.mark.asyncio
    async def test_create_task_unauthorized(self, client):
        """Test creating task without authentication."""
        task_data = {"title": "New Task"}
        response = await client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_create_task_invalid_data(self, auth_client):
        """Test creating task with invalid data."""
        task_data = {"title": ""}  # Empty title
        response = await auth_client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_task_missing_title(self, auth_client):
        """Test creating task without required title."""
        task_data = {"description": "Description without title"}
        response = await auth_client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_task_invalid_status(self, auth_client):
        """Test creating task with invalid status."""
        task_data = {"title": "Task with invalid status", "status": "invalid_status"}
        response = await auth_client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_get_task_success(self, auth_client, test_task):
        """Test getting specific task successfully."""
        response = await auth_client.get(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == test_task.title
        assert data["id"] == test_task.id
        assert data["owner_id"] == test_task.owner_id
        assert "owner" in data
        assert data["owner"]["email"] is not None

    @pytest.mark.asyncio
    async def test_get_task_unauthorized(self, client, test_task):
        """Test getting task without authentication."""
        response = await client.get(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, auth_client):
        """Test getting non-existent task."""
        response = await auth_client.get("/api/v1/tasks/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_task_other_user(self, auth_client, test_db, test_admin):
        """Test getting task owned by another user."""
        from app.services.task_service import TaskService
        from app.schemas.task import TaskCreate

        # Create task with admin user
        task_data = TaskCreate(title="Admin Task", description="Admin Description")
        admin_task = await TaskService.create(test_db, task_data, test_admin.id)

        # Try to access as regular user
        response = await auth_client.get(f"/api/v1/tasks/{admin_task.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_task_admin_access_other_user(self, admin_client, test_task):
        """Test admin accessing task owned by another user."""
        response = await admin_client.get(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_task.id

    @pytest.mark.asyncio
    async def test_update_task_success(self, auth_client, test_task):
        """Test updating task successfully."""
        update_data = {
            "title": "Updated Task",
            "description": "Updated Description",
            "status": TaskStatus.IN_PROGRESS,
        }
        response = await auth_client.put(
            f"/api/v1/tasks/{test_task.id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated Description"
        assert data["status"] == TaskStatus.IN_PROGRESS
        assert data["id"] == test_task.id

    @pytest.mark.asyncio
    async def test_partial_update_task(self, auth_client, test_task):
        """Test partial task update using PATCH."""
        update_data = {"status": TaskStatus.DONE}
        response = await auth_client.patch(
            f"/api/v1/tasks/{test_task.id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == TaskStatus.DONE
        assert data["title"] == test_task.title  # Unchanged
        assert data["description"] == test_task.description  # Unchanged

    @pytest.mark.asyncio
    async def test_update_task_unauthorized(self, client, test_task):
        """Test updating task without authentication."""
        update_data = {"title": "Updated"}
        response = await client.put(f"/api/v1/tasks/{test_task.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, auth_client):
        """Test updating non-existent task."""
        update_data = {"title": "Updated"}
        response = await auth_client.put("/api/v1/tasks/9999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_task_other_user(self, auth_client, test_db, test_admin):
        """Test updating task owned by another user."""
        from app.services.task_service import TaskService
        from app.schemas.task import TaskCreate

        # Create task with admin user
        task_data = TaskCreate(title="Admin Task", description="Admin Description")
        admin_task = await TaskService.create(test_db, task_data, test_admin.id)

        # Try to update as regular user
        update_data = {"title": "Updated by other user"}
        response = await auth_client.put(
            f"/api/v1/tasks/{admin_task.id}", json=update_data
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_update_task_admin_access_other_user(self, admin_client, test_task):
        """Test admin updating task owned by another user."""
        update_data = {"title": "Admin Updated Task"}
        response = await admin_client.put(
            f"/api/v1/tasks/{test_task.id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Admin Updated Task"

    @pytest.mark.asyncio
    async def test_delete_task_success(self, auth_client, test_task):
        """Test deleting task successfully."""
        response = await auth_client.delete(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()

        # Verify task is actually deleted
        get_response = await auth_client.get(f"/api/v1/tasks/{test_task.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_task_unauthorized(self, client, test_task):
        """Test deleting task without authentication."""
        response = await client.delete(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, auth_client):
        """Test deleting non-existent task."""
        response = await auth_client.delete("/api/v1/tasks/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_task_other_user(self, auth_client, test_db, test_admin):
        """Test deleting task owned by another user."""
        from app.services.task_service import TaskService
        from app.schemas.task import TaskCreate

        # Create task with admin user
        task_data = TaskCreate(title="Admin Task", description="Admin Description")
        admin_task = await TaskService.create(test_db, task_data, test_admin.id)

        # Try to delete as regular user
        response = await auth_client.delete(f"/api/v1/tasks/{admin_task.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_task_admin_access_other_user(self, admin_client, test_task):
        """Test admin deleting task owned by another user."""
        response = await admin_client.delete(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_task_lifecycle(self, auth_client, test_user):
        """Test complete task lifecycle: create → read → update → delete."""
        # Create task
        task_data = {
            "title": "Lifecycle Task",
            "description": "Lifecycle Description",
            "status": TaskStatus.TODO,
        }
        create_response = await auth_client.post("/api/v1/tasks/", json=task_data)
        assert create_response.status_code == status.HTTP_200_OK
        task_id = create_response.json()["id"]

        # Read task
        get_response = await auth_client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["title"] == "Lifecycle Task"

        # Update task
        update_data = {"status": TaskStatus.IN_PROGRESS}
        update_response = await auth_client.patch(
            f"/api/v1/tasks/{task_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["status"] == TaskStatus.IN_PROGRESS

        # Delete task
        delete_response = await auth_client.delete(f"/api/v1/tasks/{task_id}")
        assert delete_response.status_code == status.HTTP_200_OK

        # Verify deletion
        final_get_response = await auth_client.get(f"/api/v1/tasks/{task_id}")
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_task_status_enum_values(self, auth_client):
        """Test creating tasks with all possible status values."""
        status_values = [status.value for status in TaskStatus]

        for status_value in status_values:
            task_data = {
                "title": f"Task with status {status_value}",
                "status": status_value,
            }
            response = await auth_client.post("/api/v1/tasks/", json=task_data)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["status"] == status_value
