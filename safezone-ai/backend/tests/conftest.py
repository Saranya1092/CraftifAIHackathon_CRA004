"""Shared pytest fixtures for backend tests."""
from __future__ import annotations

import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Use an in-memory database for tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# Override settings BEFORE importing app
os.environ.setdefault("DATABASE_URL", TEST_DB_URL)
os.environ.setdefault("MQTT_BROKER_HOST", "localhost")
os.environ.setdefault("PERCEPTION_ADAPTER", "simulated")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from app.database.base import Base
from app.main import app
from app.database import base as db_base


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    from app.models import incident, zone  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    session_factory = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(db_engine):
    """HTTP test client with in-memory database injected."""
    from app.database.base import get_db

    session_factory = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Patch init_db to use test engine
    original_engine = db_base.engine
    db_base.engine = db_engine

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    db_base.engine = original_engine
