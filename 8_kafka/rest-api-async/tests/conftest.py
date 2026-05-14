"""Фикстуры для тестов."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.users import current_superuser
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

_SQLITE_URL = 'sqlite+aiosqlite:///:memory:'


def _make_superuser() -> User:
    user = User()
    user.id = uuid.uuid4()
    user.email = 'admin@test.com'
    user.is_active = True
    user.is_superuser = True
    user.is_verified = True
    return user


@pytest_asyncio.fixture
async def db_engine():
    """Создаёт SQLite движок в памяти для одного теста."""
    engine = create_async_engine(_SQLITE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Предоставляет тестовую сессию БД."""
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """HTTP клиент с подменой БД, суперюзера и Kafka producer."""
    superuser = _make_superuser()

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[current_superuser] = lambda: superuser

    # Kafka producer не нужен в тестах
    with patch('app.kafka.producer.start_producer', new_callable=AsyncMock), \
            patch('app.kafka.producer.stop_producer', new_callable=AsyncMock):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test',
        ) as ac:
            yield ac

    app.dependency_overrides.clear()
