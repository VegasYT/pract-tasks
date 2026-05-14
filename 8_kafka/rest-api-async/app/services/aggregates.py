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
from app.schemas.industry import IndustryPercentSchema

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


def _percent(part: int, total: int) -> float | None:
    """Вычисляет процент part от total. Возвращает None если total == 0."""
    if total == 0:
        return None
    return round(part / total * 100, 2)  # noqa: WPS432


def _build_totals(rows) -> dict:  # noqa: WPS110
    return {
        'total': sum(row.total_companies for row in rows),
        'business': sum(row.companies_with_business_value for row in rows),
        'profit': sum(row.companies_with_profit for row in rows),
        'no_debt': sum(row.companies_without_debt for row in rows),
        'solvency': sum(row.companies_with_solvency_rank for row in rows),
        'roa': sum(row.companies_with_roa for row in rows),
    }


def _row_to_schema(row, totals: dict) -> IndustryPercentSchema:
    return IndustryPercentSchema(
        industry_id=row.industry_id,
        industry_name=row.industry,
        total_companies=_percent(
            row.total_companies, totals['total'],
        ),
        companies_with_business_value=_percent(
            row.companies_with_business_value, totals['business'],
        ),
        companies_with_profit=_percent(
            row.companies_with_profit, totals['profit'],
        ),
        companies_without_debt=_percent(
            row.companies_without_debt, totals['no_debt'],
        ),
        companies_with_solvency_rank=_percent(
            row.companies_with_solvency_rank, totals['solvency'],
        ),
        companies_with_roa=_percent(
            row.companies_with_roa, totals['roa'],
        ),
    )


async def get_industry_percent(
    session: AsyncSession,
    industry_ids: list[int],
) -> list[IndustryPercentSchema]:
    """Возвращает процентные доли компаний отраслей от суммарных значений.

    Несуществующие id пропускаются.
    """
    rows = await common_info_industry_repo.get_by_industry_ids(
        session, industry_ids,
    )

    if not rows:
        return []

    totals = _build_totals(rows)
    logger.info(
        'industry percent: ids=%s, found=%d rows', industry_ids, len(rows),
    )
    return [_row_to_schema(row, totals) for row in rows]
