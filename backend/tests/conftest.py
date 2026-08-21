"""Shared fixtures: isolated in-memory SQLite database + authenticated API clients."""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import User, UserRole
from app.services.auth import AuthService

ADMIN_PASSWORD = "Admin1234!"
VIEWER_PASSWORD = "Viewer1234!"


@pytest_asyncio.fixture()
async def db_sessionmaker():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture()
async def users(db_sessionmaker):
    async with db_sessionmaker() as session:
        admin = User(
            username="admin",
            email="admin@urbantraffic.local",
            hashed_password=AuthService.get_password_hash(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        viewer = User(
            username="viewer",
            email="viewer@urbantraffic.local",
            hashed_password=AuthService.get_password_hash(VIEWER_PASSWORD),
            role=UserRole.VIEWER,
            is_active=True,
        )
        session.add_all([admin, viewer])
        await session.commit()


@pytest_asyncio.fixture()
async def client(db_sessionmaker, users):
    async def override_get_db():
        async with db_sessionmaker() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()


async def _auth_header(client: AsyncClient, username: str, password: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture()
async def admin_headers(client):
    return await _auth_header(client, "admin", ADMIN_PASSWORD)


@pytest_asyncio.fixture()
async def viewer_headers(client):
    return await _auth_header(client, "viewer", VIEWER_PASSWORD)
