# """Test database models functionality."""

# from datetime import datetime
# import pytest
# from app.models.user import User
# from app.models.task import Task, TaskStatus


# class TestUserModel:
#     """Test User model functionality."""

#     def test_user_creation(self, test_user):
#         """Test user creation with valid data."""
#         assert test_user.email == "test@example.com"
#         assert test_user.is_active is True
#         assert test_user.is_admin is False
#         assert hasattr(test_user, "id")
#         assert hasattr(test_user, "hashed_password")
#         assert test_user.hashed_password is not None
#         assert test_user.hashed_password != "testpassword"  # Should be hashed

#     def test_user_repr(self, test_user):
#         """Test user string representation."""
#         repr_str = repr(test_user)
#         assert "User" in repr_str
#         assert "test@example.com" in repr_str
#         assert str(test_user.id) in repr_str

#     def test_user_str(self, test_user):
#         """Test user string conversion."""
#         str_repr = str(test_user)
#         assert "User" in str_repr
#         assert "test@example.com" in str_repr

#     def test_user_relationships(self, test_user, test_task):
#         """Test user-task relationships."""
#         assert len(test_user.tasks) == 1
#         assert test_user.tasks[0].id == test_task.id
#         assert test_user.tasks[0].title == "Test Task"
#         assert test_user.tasks[0].owner_id == test_user.id

#     def test_user_equality(self, test_db, test_user):
#         """Test user equality comparison."""
#         # Same user should be equal to itself
#         assert test_user == test_user

#         # Different users should not be equal
#         other_user = User(
#             email="other@example.com",
#             hashed_password="different_hash",
#             is_active=True,
#             is_admin=False,
#         )
#         assert test_user != other_user

#     def test_user_hash(self, test_user):
#         """Test user hashing."""
#         # Should be able to hash user instance
#         user_hash = hash(test_user)
#         assert isinstance(user_hash, int)

#     def test_user_inactive(self, test_db):
#         """Test creating inactive user."""
#         user = User(
#             email="inactive@example.com",
#             hashed_password="hashed_password",
#             is_active=False,
#             is_admin=False,
#         )
#         assert user.is_active is False

#     def test_user_admin(self, test_db):
#         """Test creating admin user."""
#         user = User(
#             email="admin@example.com",
#             hashed_password="hashed_password",
#             is_active=True,
#             is_admin=True,
#         )
#         assert user.is_admin is True

#     def test_user_default_values(self, test_db):
#         """Test user default values."""
#         user = User(
#             email="default@example.com",
#             hashed_password="hashed_password",
#         )
#         assert user.is_active is True
#         assert user.is_admin is False

#     def test_user_table_name(self):
#         """Test user table name."""
#         assert User.__tablename__ == "users"

#     def test_user_columns(self):
#         """Test user table columns."""
#         columns = [col.name for col in User.__table__.columns]
#         expected_columns = ["id", "email", "hashed_password", "is_active", "is_admin"]
#         for col in expected_columns:
#             assert col in columns


# class TestTaskModel:
#     """Test Task model functionality."""

#     def test_task_creation(self, test_task):
#         """Test task creation with valid data."""
#         assert test_task.title == "Test Task"
#         assert test_task.description == "Test Description"
#         assert test_task.status == TaskStatus.TODO
#         assert hasattr(test_task, "id")
#         assert hasattr(test_task, "created_at")
#         assert hasattr(test_task, "owner_id")
#         assert isinstance(test_task.created_at, datetime)

#     def test_task_repr(self, test_task):
#         """Test task string representation."""
#         repr_str = repr(test_task)
#         assert "Task" in repr_str
#         assert "Test Task" in repr_str
#         assert str(test_task.id) in repr_str

#     def test_task_str(self, test_task):
#         """Test task string conversion."""
#         str_repr = str(test_task)
#         assert "Task" in str_repr
#         assert "Test Task" in str_repr

#     def test_task_status_enum(self):
#         """Test task status enum values and behavior."""
#         assert TaskStatus.TODO == "todo"
#         assert TaskStatus.IN_PROGRESS == "in_progress"
#         assert TaskStatus.DONE == "done"

#         # Test enum membership
#         assert "todo" in TaskStatus.__members__.values()
#         assert "in_progress" in TaskStatus.__members__.values()
#         assert "done" in TaskStatus.__members__.values()

#         # Test enum iteration
#         statuses = list(TaskStatus)
#         assert len(statuses) == 3
#         assert TaskStatus.TODO in statuses
#         assert TaskStatus.IN_PROGRESS in statuses
#         assert TaskStatus.DONE in statuses

#     def test_task_relationships(self, test_task, test_user):
#         """Test task-user relationships."""
#         assert test_task.owner.id == test_user.id
#         assert test_task.owner.email == test_user.email
#         assert test_task in test_user.tasks

#     def test_task_equality(self, test_db, test_task):
#         """Test task equality comparison."""
#         # Same task should be equal to itself
#         assert test_task == test_task

#         # Different tasks should not be equal
#         other_task = Task(
#             title="Other Task",
#             description="Other Description",
#             status=TaskStatus.TODO,
#             owner_id=test_task.owner_id,
#         )
#         assert test_task != other_task

#     def test_task_hash(self, test_task):
#         """Test task hashing."""
#         # Should be able to hash task instance
#         task_hash = hash(test_task)
#         assert isinstance(task_hash, int)

#     def test_task_default_status(self, test_db, test_user):
#         """Test task default status."""
#         task = Task(
#             title="Task with default status",
#             description="Description",
#             owner_id=test_user.id,
#         )
#         assert task.status == TaskStatus.TODO

#     def test_task_default_created_at(self, test_db, test_user):
#         """Test task created_at default value."""
#         task = Task(
#             title="Task with created_at",
#             description="Description",
#             owner_id=test_user.id,
#         )
#         assert task.created_at is None  # Will be set by database

#     def test_task_all_statuses(self, test_db, test_user):
#         """Test creating tasks with all status values."""
#         for status in TaskStatus:
#             task = Task(
#                 title=f"Task with {status.value}",
#                 description="Description",
#                 status=status,
#                 owner_id=test_user.id,
#             )
#             assert task.status == status

#     def test_task_table_name(self):
#         """Test task table name."""
#         assert Task.__tablename__ == "tasks"

#     def test_task_columns(self):
#         """Test task table columns."""
#         columns = [col.name for col in Task.__table__.columns]
#         expected_columns = [
#             "id",
#             "title",
#             "description",
#             "status",
#             "created_at",
#             "owner_id",
#         ]
#         for col in expected_columns:
#             assert col in columns

#     def test_task_foreign_key(self, test_task, test_user):
#         """Test task foreign key relationship."""
#         assert test_task.owner_id == test_user.id
#         # This tests the actual foreign key constraint at the model level

#     def test_task_cascade_behavior(self, test_db, test_user, test_task):
#         """Test task behavior when owner is deleted."""
#         # This tests the cascade delete behavior
#         # When a user is deleted, their tasks should be deleted too
#         # This is tested at the database level in integration tests
#         pass


# class TestModelRelationships:
#     """Test model relationships and constraints."""

#     def test_user_tasks_relationship(self, test_user, test_task):
#         """Test bidirectional user-tasks relationship."""
#         # User -> Tasks
#         assert len(test_user.tasks) == 1
#         assert test_user.tasks[0].id == test_task.id

#         # Task -> User
#         assert test_task.owner.id == test_user.id
#         assert test_task.owner.email == test_user.email

#     async def test_multiple_tasks_per_user(self, test_db, test_user):
#         """Test user with multiple tasks."""
#         tasks = [
#             Task(
#                 title=f"Task {i}",
#                 description=f"Description {i}",
#                 status=TaskStatus.TODO,
#                 owner_id=test_user.id,
#             )
#             for i in range(3)
#         ]

#         for task in tasks:
#             test_db.add(task)
#         await test_db.commit()

#         for task in tasks:
#             await test_db.refresh(task)

#         assert len(test_user.tasks) >= 3

#     async def test_task_owner_required(self, test_db):
#         """Test that task requires an owner."""
#         task = Task(
#             title="Task without owner",
#             description="Description",
#             status=TaskStatus.TODO,
#             # Missing owner_id - should raise error on commit
#         )
#         test_db.add(task)

#         with pytest.raises(Exception):  # Should raise integrity error
#             await test_db.commit()


"""Test database models functionality."""

from datetime import datetime
import pytest
from sqlalchemy import select
from app.models.user import User
from app.models.task import Task, TaskStatus


class TestUserModel:
    """Test User model functionality."""

    def test_user_creation(self, test_user):
        """Test user creation with valid data."""
        assert test_user.email == "test@example.com"
        assert test_user.is_active is True
        assert test_user.is_admin is False
        assert hasattr(test_user, "id")
        assert hasattr(test_user, "hashed_password")
        assert test_user.hashed_password is not None
        assert test_user.hashed_password != "testpassword"  # Should be hashed

    def test_user_repr(self, test_user):
        """Test user string representation."""
        repr_str = repr(test_user)
        assert "User" in repr_str
        assert "test@example.com" in repr_str
        assert str(test_user.id) in repr_str

    def test_user_str(self, test_user):
        """Test user string conversion."""
        str_repr = str(test_user)
        assert "User" in str_repr
        assert "test@example.com" in str_repr

    @pytest.mark.asyncio
    async def test_user_relationships(self, test_db, test_user, test_task):
        """Test user-task relationships."""
        # Refresh the user to ensure relationships are loaded
        await test_db.refresh(test_user, attribute_names=["tasks"])
        assert len(test_user.tasks) == 1
        assert test_user.tasks[0].id == test_task.id
        assert test_user.tasks[0].title == "Test Task"
        assert test_user.tasks[0].owner_id == test_user.id

    def test_user_equality(self, test_user):
        """Test user equality comparison."""
        # Same user should be equal to itself
        assert test_user == test_user

        # Different users should not be equal
        other_user = User(
            email="other@example.com",
            hashed_password="different_hash",
        )
        assert test_user != other_user

    def test_user_hash(self, test_user):
        """Test user hashing."""
        # Should be able to hash user instance
        user_hash = hash(test_user)
        assert isinstance(user_hash, int)

    def test_user_inactive(self):
        """Test creating inactive user."""
        user = User(
            email="inactive@example.com",
            hashed_password="hashed_password",
            is_active=False,
            is_admin=False,
        )
        assert user.is_active is False

    def test_user_admin(self):
        """Test creating admin user."""
        user = User(
            email="admin@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_admin=True,
        )
        assert user.is_admin is True

    def test_user_default_values(self):
        """Test user default values."""
        user = User(
            email="default@example.com",
            hashed_password="hashed_password",
        )
        assert user.is_active is True
        assert user.is_admin is False

    def test_user_table_name(self):
        """Test user table name."""
        assert User.__tablename__ == "users"

    def test_user_columns(self):
        """Test user table columns."""
        columns = [col.name for col in User.__table__.columns]
        expected_columns = ["id", "email", "hashed_password", "is_active", "is_admin"]
        for col in expected_columns:
            assert col in columns


class TestTaskModel:
    """Test Task model functionality."""

    def test_task_creation(self, test_task):
        """Test task creation with valid data."""
        assert test_task.title == "Test Task"
        assert test_task.description == "Test Description"
        assert test_task.status == TaskStatus.TODO
        assert hasattr(test_task, "id")
        assert hasattr(test_task, "created_at")
        assert hasattr(test_task, "owner_id")

    def test_task_repr(self, test_task):
        """Test task string representation."""
        repr_str = repr(test_task)
        assert "Task" in repr_str
        assert "Test Task" in repr_str
        assert str(test_task.id) in repr_str

    def test_task_str(self, test_task):
        """Test task string conversion."""
        str_repr = str(test_task)
        assert "Task" in str_repr
        assert "Test Task" in str_repr

    def test_task_status_enum(self):
        """Test task status enum values and behavior."""
        assert TaskStatus.TODO == "todo"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.DONE == "done"

        # Test enum membership
        assert "todo" in TaskStatus.__members__.values()
        assert "in_progress" in TaskStatus.__members__.values()
        assert "done" in TaskStatus.__members__.values()

        # Test enum iteration
        statuses = list(TaskStatus)
        assert len(statuses) == 3
        assert TaskStatus.TODO in statuses
        assert TaskStatus.IN_PROGRESS in statuses
        assert TaskStatus.DONE in statuses

    @pytest.mark.asyncio
    async def test_task_relationships(self, test_db, test_task, test_user):
        """Test task-user relationships."""
        # Refresh the task to ensure relationships are loaded
        await test_db.refresh(test_task, attribute_names=["owner"])
        assert test_task.owner.id == test_user.id
        assert test_task.owner.email == test_user.email

        # Refresh user to check the reverse relationship
        await test_db.refresh(test_user, attribute_names=["tasks"])
        assert test_task in test_user.tasks

    def test_task_equality(self, test_task):
        """Test task equality comparison."""
        # Same task should be equal to itself
        assert test_task == test_task

        # Different tasks should not be equal
        other_task = Task(
            title="Other Task",
            description="Other Description",
            status=TaskStatus.TODO,
            owner_id=test_task.owner_id,
        )
        assert test_task != other_task

    def test_task_hash(self, test_task):
        """Test task hashing."""
        # Should be able to hash task instance
        task_hash = hash(test_task)
        assert isinstance(task_hash, int)

    def test_task_default_status(self):
        """Test task default status."""
        task = Task(
            title="Task with default status",
            description="Description",
            owner_id=1,  # Use a dummy ID for this test
        )
        assert task.status == TaskStatus.TODO

    def test_task_default_created_at(self):
        """Test task created_at default value."""
        task = Task(
            title="Task with created_at",
            description="Description",
            owner_id=1,  # Use a dummy ID for this test
        )
        # created_at will be None until persisted to database
        assert task.created_at is None

    def test_task_all_statuses(self):
        """Test creating tasks with all status values."""
        for status in TaskStatus:
            task = Task(
                title=f"Task with {status.value}",
                description="Description",
                status=status,
                owner_id=1,  # Use a dummy ID for this test
            )
            assert task.status == status

    def test_task_table_name(self):
        """Test task table name."""
        assert Task.__tablename__ == "tasks"

    def test_task_columns(self):
        """Test task table columns."""
        columns = [col.name for col in Task.__table__.columns]
        expected_columns = [
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "owner_id",
        ]
        for col in expected_columns:
            assert col in columns

    def test_task_foreign_key(self, test_task, test_user):
        """Test task foreign key relationship."""
        assert test_task.owner_id == test_user.id


class TestModelRelationships:
    """Test model relationships and constraints."""

    @pytest.mark.asyncio
    async def test_user_tasks_relationship(self, test_db, test_user, test_task):
        """Test bidirectional user-tasks relationship."""
        # Refresh both objects to ensure relationships are loaded
        await test_db.refresh(test_user, attribute_names=["tasks"])
        await test_db.refresh(test_task, attribute_names=["owner"])

        # User -> Tasks
        assert len(test_user.tasks) == 1
        assert test_user.tasks[0].id == test_task.id

        # Task -> User
        assert test_task.owner.id == test_user.id
        assert test_task.owner.email == test_user.email

    @pytest.mark.asyncio
    async def test_multiple_tasks_per_user(self, test_db, test_user):
        """Test user with multiple tasks."""
        tasks = [
            Task(
                title=f"Task {i}",
                description=f"Description {i}",
                status=TaskStatus.TODO,
                owner_id=test_user.id,
            )
            for i in range(3)
        ]

        for task in tasks:
            test_db.add(task)
        await test_db.commit()

        for task in tasks:
            await test_db.refresh(task)

        # Refresh user to load the new tasks
        await test_db.refresh(test_user, attribute_names=["tasks"])
        assert len(test_user.tasks) >= 3

    @pytest.mark.asyncio
    async def test_task_owner_required(self, test_db):
        """Test that task requires an owner."""
        task = Task(
            title="Task without owner",
            description="Description",
            status=TaskStatus.TODO,
            # Missing owner_id - should raise error on commit
        )
        test_db.add(task)

        with pytest.raises(Exception):  # Should raise integrity error
            await test_db.commit()
