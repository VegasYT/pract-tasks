"""Фикстуры для тестов."""

import io

import pandas as pd
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app

_SQLITE_URL = 'sqlite+aiosqlite:///:memory:'


@pytest_asyncio.fixture
async def db_engine():
    """Создаёт асинхронный SQLite движок для одного теста."""
    engine = create_async_engine(_SQLITE_URL)
    async with engine.begin() as setup_conn:
        await setup_conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as teardown_conn:
        await teardown_conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Предоставляет тестовую сессию БД."""
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Предоставляет тестовый HTTP клиент с подменой зависимости БД."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def sample_csv() -> bytes:
    """Минимальный валидный CSV с одной строкой данных."""
    columns = [  # noqa: WPS317
        'ID',
        'оквэд',
        'расшифровка оквэд',
        'Отрасль',
        'Субъект',
        'Округ',
        'текущая стоимость бизнеса',
        'ликвидационная стоимость бизнеса',
        'расчёт возвратности средств для кредиторов',
        'потребность в оборотных средствах',
        'прибыль до налогообложения',
        'задолженность по налогам',
        'исполнительное производство без учета налогов',
        'Лимит поручительства',
        'ранг платёжеспособности',
        'возраст организации',
        'возбуждено производство по делу о несостоятельности (банкротстве)',
        'иностранные лица в органах управления',
    ]
    zero = 0.0  # noqa: WPS358
    business_value = 41000.0  # noqa: WPS358
    solvency = 6.24  # noqa: WPS358
    age = 0.81  # noqa: WPS358
    row = [  # noqa: WPS317, WPS210
        1000000001,
        '01.13.3',
        'Test description',
        'Test industry',
        'Test subject',
        'Test district',
        business_value,
        zero, zero, zero, zero, zero, zero,
        'не может быть поручителем',
        solvency,
        age,
        zero, zero,
    ]
    data_frame = pd.DataFrame([row], columns=columns)
    buffer = io.BytesIO()
    data_frame.to_csv(buffer, encoding='utf-8')
    return buffer.getvalue()
