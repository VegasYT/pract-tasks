"""Репозиторий для работы с таблицей RegionDataORM."""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import RegionDataORM


async def clear_table(session: AsyncSession) -> None:
    """Очищает таблицу region_data."""
    await session.execute(delete(RegionDataORM))


async def bulk_insert(
    session: AsyncSession,
    records: list[dict],
) -> None:
    """Массово вставляет записи в таблицу region_data."""
    session.add_all([RegionDataORM(**record) for record in records])
