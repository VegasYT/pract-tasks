"""Репозиторий для работы с таблицей CompanyDataORM."""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import CompanyDataORM


async def clear_table(session: AsyncSession) -> None:
    """Очищает таблицу company_data."""
    await session.execute(delete(CompanyDataORM))


async def bulk_insert(
    session: AsyncSession,
    records: list[dict],
) -> None:
    """Массово вставляет записи в таблицу company_data."""
    session.add_all([CompanyDataORM(**record) for record in records])
