"""Pytest configuration and fixtures for testing the FastAPI application."""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.config import settings
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.auth.security import get_password_hash


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh test database for each test function."""
    # Configure test database
    test_database_url = "sqlite+aiosqlite:///:memory:"

    engine = create_async_engine(
        test_database_url,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create async session factory
    TestingSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create session
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with test database."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield test_db
        finally:
            await test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Create a fresh client WITHOUT any headers
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("Testpassword123"),
        is_active=True,
        is_admin=False,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(test_db: AsyncSession) -> User:
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("Adminpassword123"),
        is_active=True,
        is_admin=True,
    )
    test_db.add(admin)
    await test_db.commit()
    await test_db.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def test_task(test_db: AsyncSession, test_user: User) -> Task:
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        owner_id=test_user.id,
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    return task


@pytest_asyncio.fixture
async def auth_client(
    test_db: AsyncSession, test_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated test client."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield test_db
        finally:
            await test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Create a temporary client for login
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as temp_client:
        # Login to get token
        login_data = {"username": test_user.email, "password": "Testpassword123"}
        response = await temp_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

    # Create a SEPARATE client with auth headers
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_client(
    test_db: AsyncSession, test_admin: User
) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated admin test client."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield test_db
        finally:
            await test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Create a temporary client for login
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as temp_client:
        # Login to get token
        login_data = {"username": test_admin.email, "password": "Adminpassword123"}
        response = await temp_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

    # Create a SEPARATE client with auth headers
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def another_user(test_db: AsyncSession) -> User:
    """Create another test user for testing multi-user scenarios."""
    user = User(
        email="another@example.com",
        hashed_password=get_password_hash("Anotherpassword123"),
        is_active=True,
        is_admin=False,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def multiple_tasks(test_db: AsyncSession, test_user: User) -> list[Task]:
    """Create multiple test tasks."""
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

    return tasks


@pytest_asyncio.fixture
async def unauthenticated_client(
    test_db: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Create a guaranteed unauthenticated test client."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield test_db
        finally:
            await test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Create a fresh client WITHOUT any headers
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()
