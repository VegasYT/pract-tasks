"""Репозиторий для работы с таблицей CountyDataORM."""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.county import CountyDataORM


async def clear_table(session: AsyncSession) -> None:
    """Очищает таблицу county_data."""
    await session.execute(delete(CountyDataORM))


async def bulk_insert(
    session: AsyncSession,
    records: list[dict],
) -> None:
    """Массово вставляет записи в таблицу county_data."""
    session.add_all([CountyDataORM(**record) for record in records])
