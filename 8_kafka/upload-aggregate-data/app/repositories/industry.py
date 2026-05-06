"""Репозитории для таблиц industry_data и common_info_industry."""

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import CompanyDataORM
from app.models.industry import CommonInfoIndustry, IndustryDataORM
from app.repositories.base import BaseRepository

_WITH_VALUE = case((CompanyDataORM.current_business_value > 0, 1), else_=0)
_WITH_PROFIT = case((CompanyDataORM.profit_before_tax > 0, 1), else_=0)
_WITH_RANK = case((CompanyDataORM.solvency_rank > 0, 1), else_=0)
_WITH_ROA = case((CompanyDataORM.creditor_return_rate != 0, 1), else_=0)
_NO_DEBT = and_(
    func.coalesce(CompanyDataORM.tax_debt, 0) == 0,
    func.coalesce(CompanyDataORM.enforcement_debt, 0) == 0,
)


class IndustryCommonInfoRepository(BaseRepository[CommonInfoIndustry]):
    """Репозиторий common_info_industry с методом агрегации из компаний."""

    async def compute_from_companies(
        self,
        session: AsyncSession,
    ) -> list[dict]:
        """Считает счётчики по отраслям через JOIN company -> industry_data.

        Returns:
            Список словарей со счётчиками и industry_id.
        """
        subq = select(
            CompanyDataORM.industry,
            func.count().label('total_companies'),
            func.sum(_WITH_VALUE).label('companies_with_business_value'),
            func.sum(_WITH_PROFIT).label('companies_with_profit'),
            func.sum(
                case((_NO_DEBT, 1), else_=0),
            ).label('companies_without_debt'),
            func.sum(_WITH_RANK).label('companies_with_solvency_rank'),
            func.sum(_WITH_ROA).label('companies_with_roa'),
        ).group_by(CompanyDataORM.industry).subquery()
        stmt = select(subq, IndustryDataORM.id.label('industry_id')).join(
            IndustryDataORM, IndustryDataORM.industry == subq.c.industry,
        )
        rows = await session.execute(stmt)
        return [dict(row._mapping) for row in rows]  # noqa: WPS437


industry_repository = BaseRepository(IndustryDataORM)
common_info_industry_repository = IndustryCommonInfoRepository(
    CommonInfoIndustry,
)
