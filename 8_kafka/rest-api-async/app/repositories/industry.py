"""Репозиторий для таблиц industry_data и common_info_industry."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.industry import CommonInfoIndustry, IndustryDataORM
from app.repositories.base import BaseRepository


class IndustryRepository(BaseRepository[CommonInfoIndustry]):
    """Репозиторий common_info_industry с фильтрацией по id отраслей."""

    async def get_by_industry_ids(
        self,
        session: AsyncSession,
        industry_ids: list[int],
    ) -> list[CommonInfoIndustry]:
        """Возвращает строки CommonInfoIndustry для переданных id отраслей."""
        rows = await session.execute(
            select(CommonInfoIndustry).where(
                CommonInfoIndustry.industry_id.in_(industry_ids),
            ),
        )
        return list(rows.scalars().all())


industry_repository = BaseRepository(IndustryDataORM)
common_info_industry_repository = IndustryRepository(CommonInfoIndustry)
