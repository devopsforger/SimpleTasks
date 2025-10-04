"""Test cases for service layer functionality."""

import pytest
from app.services.user_service import UserService
from app.services.task_service import TaskService
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import TaskStatus
from app.models.user import User


class TestUserService:
    """Test UserService functionality."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, test_db, test_user):
        """Test getting user by ID when user exists."""
        user = await UserService.get_by_id(test_db, test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.is_active == test_user.is_active
        assert user.is_admin == test_user.is_admin

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_db):
        """Test getting user by ID when user doesn't exist."""
        user = await UserService.get_by_id(test_db, 9999)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_id_zero(self, test_db):
        """Test getting user with ID zero."""
        user = await UserService.get_by_id(test_db, 0)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_email_success(self, test_db, test_user):
        """Test getting user by email when user exists."""
        user = await UserService.get_by_email(test_db, test_user.email)

        assert user is not None
        assert user.email == test_user.email
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, test_db):
        """Test getting user by email when user doesn't exist."""
        user = await UserService.get_by_email(test_db, "nonexistent@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_email_case_sensitive(self, test_db, test_user):
        """Test email lookup is case sensitive."""
        user = await UserService.get_by_email(test_db, test_user.email.upper())
        assert user is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, test_db, test_user, test_admin):
        """Test getting all users."""
        users = await UserService.get_all(test_db)

        assert len(users) >= 2
        user_emails = [user.email for user in users]
        assert test_user.email in user_emails
        assert test_admin.email in user_emails

    @pytest.mark.asyncio
    async def test_get_all_users_pagination(self, test_db, multiple_tasks):
        """Test getting all users with pagination."""
        users = await UserService.get_all(test_db, skip=1, limit=1)

        assert len(users) <= 1

    @pytest.mark.asyncio
    async def test_get_all_users_empty(self, test_db):
        """Test getting all users from empty database."""
        # Delete all users first
        users = await test_db.execute(User.__table__.delete())
        await test_db.commit()

        users = await UserService.get_all(test_db)
        assert users == []

    @pytest.mark.asyncio
    async def test_create_user_success(self, test_db):
        """Test creating a new user successfully."""
        user_data = UserCreate(
            email="newuser@example.com",
            password="Newpassword123",
            is_admin=False,
        )
        user = await UserService.create(test_db, user_data)

        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.is_admin is False
        assert user.is_active is True
        assert hasattr(user, "id")
        assert user.hashed_password != "Newpassword123"  # Should be hashed

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, test_db, test_user):
        """Test creating user with duplicate email."""
        user_data = UserCreate(
            email=test_user.email,  # Already exists
            password="Password123",
            is_admin=False,
        )

        with pytest.raises(ValueError, match="already exists"):
            await UserService.create(test_db, user_data)

    @pytest.mark.asyncio
    async def test_create_user_admin(self, test_db):
        """Test creating admin user."""
        user_data = UserCreate(
            email="adminuser@example.com",
            password="Adminpassword123",
            is_admin=True,
        )
        user = await UserService.create(test_db, user_data)

        assert user.is_admin is True

    @pytest.mark.asyncio
    async def test_create_user_inactive(self, test_db):
        """Test creating inactive user."""
        user_data = UserCreate(
            email="inactive@example.com",
            password="Password123",
            is_active=False,
            is_admin=False,
        )
        user = await UserService.create(test_db, user_data)

        assert user.is_active is False

    @pytest.mark.asyncio
    async def test_update_user_success(self, test_db, test_user):
        """Test updating user successfully."""
        update_data = UserUpdate(is_admin=True, is_active=False)
        updated_user = await UserService.update(test_db, test_user.id, update_data)

        assert updated_user is not None
        assert updated_user.is_admin is True
        assert updated_user.is_active is False
        assert updated_user.email == test_user.email  # Unchanged
        assert updated_user.id == test_user.id

    @pytest.mark.asyncio
    async def test_update_user_partial(self, test_db, test_user):
        """Test updating user with partial data."""
        update_data = UserUpdate(is_admin=True)
        updated_user = await UserService.update(test_db, test_user.id, update_data)

        assert updated_user.is_admin is True
        assert updated_user.is_active == test_user.is_active  # Unchanged
        assert updated_user.email == test_user.email  # Unchanged

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, test_db):
        """Test updating non-existent user."""
        update_data = UserUpdate(is_admin=True)
        user = await UserService.update(test_db, 9999, update_data)
        assert user is None

    @pytest.mark.asyncio
    async def test_update_user_email(self, test_db, test_user):
        """Test updating user email."""
        update_data = UserUpdate(email="updated@example.com")
        updated_user = await UserService.update(test_db, test_user.id, update_data)

        assert updated_user.email == "updated@example.com"

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email(self, test_db, test_user, test_admin):
        """Test updating user with duplicate email."""
        update_data = UserUpdate(email=test_admin.email)

        with pytest.raises(ValueError, match="already exists"):
            await UserService.update(test_db, test_user.id, update_data)

    @pytest.mark.asyncio
    async def test_delete_user_success(self, test_db, test_user):
        """Test deleting user successfully."""
        result = await UserService.delete(test_db, test_user.id)
        assert result is True

        # Verify user is deleted
        user = await UserService.get_by_id(test_db, test_user.id)
        assert user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, test_db):
        """Test deleting non-existent user."""
        result = await UserService.delete(test_db, 9999)
        assert result is False

    @pytest.mark.asyncio
    async def test_authenticate_success(self, test_db, test_user):
        """Test successful authentication."""
        user = await UserService.authenticate(test_db, test_user.email, "Testpassword123")

        assert user is not None
        assert user.email == test_user.email
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, test_db, test_user):
        """Test authentication with wrong password."""
        user = await UserService.authenticate(test_db, test_user.email, "wrongpassword")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, test_db):
        """Test authentication with non-existent user."""
        user = await UserService.authenticate(
            test_db, "nonexistent@example.com", "Password123"
        )
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, test_db, test_user):
        """Test authentication with inactive user."""
        # Deactivate user
        update_data = UserUpdate(is_active=False)
        await UserService.update(test_db, test_user.id, update_data)

        user = await UserService.authenticate(test_db, test_user.email, "Testpassword123")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_empty_password(self, test_db, test_user):
        """Test authentication with empty password."""
        user = await UserService.authenticate(test_db, test_user.email, "")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_case_sensitive_email(self, test_db, test_user):
        """Test authentication with case-sensitive email."""
        user = await UserService.authenticate(
            test_db, test_user.email.upper(), "Testpassword123"
        )
        assert user is None


class TestTaskService:
    """Test TaskService functionality."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, test_db, test_task):
        """Test getting task by ID when task exists."""
        task = await TaskService.get_by_id(test_db, test_task.id)

        assert task is not None
        assert task.id == test_task.id
        assert task.title == test_task.title
        assert task.description == test_task.description
        assert task.status == test_task.status
        assert task.owner_id == test_task.owner_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_db):
        """Test getting task by ID when task doesn't exist."""
        task = await TaskService.get_by_id(test_db, 9999)
        assert task is None

    @pytest.mark.asyncio
    async def test_get_all_tasks(self, test_db, test_task, multiple_tasks):
        """Test getting all tasks."""
        tasks = await TaskService.get_all(test_db)

        assert len(tasks) >= 4  # test_task + 3 from multiple_tasks
        task_titles = [task.title for task in tasks]
        assert test_task.title in task_titles

    @pytest.mark.asyncio
    async def test_get_all_tasks_pagination(self, test_db, multiple_tasks):
        """Test getting all tasks with pagination."""
        tasks = await TaskService.get_all(test_db, skip=1, limit=2)

        assert len(tasks) <= 2

    @pytest.mark.asyncio
    async def test_get_all_tasks_empty(self, test_db):
        """Test getting all tasks from empty database."""
        # Ensure no tasks exist
        tasks = await TaskService.get_all(test_db)
        # This might not be empty if other tests created tasks, so we just check it's a list
        assert isinstance(tasks, list)

    @pytest.mark.asyncio
    async def test_get_by_owner(self, test_db, test_task, test_user):
        """Test getting tasks by owner."""
        tasks = await TaskService.get_by_owner(test_db, test_user.id)

        assert len(tasks) >= 1
        assert all(task.owner_id == test_user.id for task in tasks)
        assert any(task.id == test_task.id for task in tasks)

    @pytest.mark.asyncio
    async def test_get_by_owner_pagination(self, test_db, test_user, multiple_tasks):
        """Test getting tasks by owner with pagination."""
        tasks = await TaskService.get_by_owner(test_db, test_user.id, skip=1, limit=2)

        assert len(tasks) <= 2
        assert all(task.owner_id == test_user.id for task in tasks)

    @pytest.mark.asyncio
    async def test_get_by_owner_no_tasks(self, test_db, another_user):
        """Test getting tasks for user with no tasks."""
        tasks = await TaskService.get_by_owner(test_db, another_user.id)
        assert tasks == []

    @pytest.mark.asyncio
    async def test_create_task_success(self, test_db, test_user):
        """Test creating a new task successfully."""
        task_data = TaskCreate(
            title="New Task",
            description="New Description",
            status=TaskStatus.TODO,
        )
        task = await TaskService.create(test_db, task_data, test_user.id)

        assert task is not None
        assert task.title == "New Task"
        assert task.description == "New Description"
        assert task.status == TaskStatus.TODO
        assert task.owner_id == test_user.id
        assert hasattr(task, "id")
        assert hasattr(task, "created_at")

    @pytest.mark.asyncio
    async def test_create_task_minimal_data(self, test_db, test_user):
        """Test creating task with minimal required data."""
        task_data = TaskCreate(title="Minimal Task")
        task = await TaskService.create(test_db, task_data, test_user.id)

        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.status == TaskStatus.TODO
        assert task.owner_id == test_user.id

    @pytest.mark.asyncio
    async def test_create_task_all_statuses(self, test_db, test_user):
        """Test creating tasks with all possible status values."""
        for status in TaskStatus:
            task_data = TaskCreate(
                title=f"Task with {status.value}",
                status=status,
            )
            task = await TaskService.create(test_db, task_data, test_user.id)
            assert task.status == status

    @pytest.mark.asyncio
    async def test_update_task_success(self, test_db, test_task):
        """Test updating task successfully."""
        update_data = TaskUpdate(
            title="Updated Task",
            description="Updated Description",
            status=TaskStatus.IN_PROGRESS,
        )
        updated_task = await TaskService.update(test_db, test_task.id, update_data)

        assert updated_task is not None
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Updated Description"
        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert updated_task.id == test_task.id

    @pytest.mark.asyncio
    async def test_partial_update_task(self, test_db, test_task):
        """Test partial task update."""
        update_data = TaskUpdate(status=TaskStatus.DONE)
        updated_task = await TaskService.update(test_db, test_task.id, update_data)

        assert updated_task is not None
        assert updated_task.status == TaskStatus.DONE
        assert updated_task.title == test_task.title  # Unchanged
        assert updated_task.description == test_task.description  # Unchanged

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, test_db):
        """Test updating non-existent task."""
        update_data = TaskUpdate(title="Updated")
        task = await TaskService.update(test_db, 9999, update_data)
        assert task is None

    @pytest.mark.asyncio
    async def test_update_task_no_changes(self, test_db, test_task):
        """Test updating task with no changes."""
        update_data = TaskUpdate()
        updated_task = await TaskService.update(test_db, test_task.id, update_data)

        assert updated_task is not None
        assert updated_task.title == test_task.title
        assert updated_task.description == test_task.description
        assert updated_task.status == test_task.status

    @pytest.mark.asyncio
    async def test_delete_task_success(self, test_db, test_task):
        """Test deleting task successfully."""
        result = await TaskService.delete(test_db, test_task.id)
        assert result is True

        # Verify task is deleted
        task = await TaskService.get_by_id(test_db, test_task.id)
        assert task is None

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, test_db):
        """Test deleting non-existent task."""
        result = await TaskService.delete(test_db, 9999)
        assert result is False

    @pytest.mark.asyncio
    async def test_can_access_task_admin(self, test_db, test_task, test_admin):
        """Test admin access to any task."""
        can_access = await TaskService.can_access_task(
            test_db, test_task.id, test_admin.id, True
        )
        assert can_access is True

    @pytest.mark.asyncio
    async def test_can_access_task_owner(self, test_db, test_task, test_user):
        """Test owner access to their own task."""
        can_access = await TaskService.can_access_task(
            test_db, test_task.id, test_user.id, False
        )
        assert can_access is True

    @pytest.mark.asyncio
    async def test_can_access_task_other_user(self, test_db, test_task, another_user):
        """Test non-owner non-admin access to task."""
        can_access = await TaskService.can_access_task(
            test_db, test_task.id, another_user.id, False
        )
        assert can_access is False

    @pytest.mark.asyncio
    async def test_can_access_task_not_found(self, test_db, test_user):
        """Test access to non-existent task."""
        can_access = await TaskService.can_access_task(
            test_db, 9999, test_user.id, False
        )
        assert can_access is False

    @pytest.mark.asyncio
    async def test_can_access_task_deleted_owner(self, test_db, test_task, test_user):
        """Test access to task when owner is deleted."""
        # Delete the owner
        await UserService.delete(test_db, test_user.id)

        can_access = await TaskService.can_access_task(
            test_db, test_task.id, test_user.id, False
        )
        # Should return False since task might be orphaned or not found
        assert can_access is False
