"""Сервис для получения агрегированных данных."""

import logging
from types import MappingProxyType

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.county import (
    common_info_county_repository as common_info_county_repo,
    county_repository as county_repo,
)
from app.repositories.industry import (
    common_info_industry_repository as common_info_industry_repo,
    industry_repository as industry_repo,
)
from app.repositories.region import (
    common_info_region_repository as common_info_region_repo,
    region_repository as region_repo,
)
from app.schemas.aggregates import (
    AggregateCountsListSchema,
    AggregateFinancialListSchema,
)

logger = logging.getLogger(__name__)

_FINANCIAL_REPOS = MappingProxyType({
    'region': region_repo,
    'county': county_repo,
    'industry': industry_repo,
})

_COUNTS_REPOS = MappingProxyType({
    'region': common_info_region_repo,
    'county': common_info_county_repo,
    'industry': common_info_industry_repo,
})


def _orm_to_dict(record) -> dict:  # noqa: WPS110
    return {
        col.name: getattr(record, col.name)
        for col in record.__table__.columns
    }


async def get_financial(
    session: AsyncSession,
    group_by: str,
) -> AggregateFinancialListSchema:
    """Возвращает финансовые суммы по выбранному разрезу."""
    records = await _FINANCIAL_REPOS[group_by].get_all(session)
    logger.info('financial aggregates fetched, group_by=%s', group_by)
    return AggregateFinancialListSchema(
        group_by=group_by,
        records=[_orm_to_dict(rec) for rec in records],
    )


async def get_counts(
    session: AsyncSession,
    group_by: str,
) -> AggregateCountsListSchema:
    """Возвращает счётчики компаний по выбранному разрезу."""
    records = await _COUNTS_REPOS[group_by].get_all(session)
    logger.info('counts aggregates fetched, group_by=%s', group_by)
    return AggregateCountsListSchema(
        group_by=group_by,
        records=[_orm_to_dict(rec) for rec in records],
    )
