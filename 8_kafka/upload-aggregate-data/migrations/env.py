"""Конфигурация окружения Alembic для асинхронного режима."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.db.base import Base
from app.models import company  # noqa: F401 - регистрируем модели в метаданных
from app.models import county  # noqa: F401 - CountyDataORM + CommonInfoCounty
from app.models import industry  # noqa: F401 - IndustryDataORM + CommonInfoIndustry
from app.models import region  # noqa: F401 - RegionDataORM + CommonInfoRegion
from app.models import user  # noqa: F401 - User

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запускает миграции в offline-режиме (без подключения к БД)."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Выполняет миграции в рамках переданного соединения."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запускает миграции в online-режиме через асинхронный движок."""
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
