"""Репозиторий для работы с таблицей CompanyDataORM."""

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import CompanyDataORM
from app.repositories.base import BaseRepository


def _common_info_columns(group_col, no_debt):  # noqa: WPS210
    """Возвращает список колонок для запроса compute_common_info."""
    return [
        group_col,
        func.count().label('total_companies'),
        func.sum(
            case((CompanyDataORM.current_business_value > 0, 1), else_=0),
        ).label('companies_with_business_value'),
        func.sum(
            case((CompanyDataORM.profit_before_tax > 0, 1), else_=0),
        ).label('companies_with_profit'),
        func.sum(
            case((no_debt, 1), else_=0),
        ).label('companies_without_debt'),
        func.sum(
            case((CompanyDataORM.solvency_rank > 0, 1), else_=0),
        ).label('companies_with_solvency_rank'),
        func.sum(
            case((CompanyDataORM.creditor_return_rate != 0, 1), else_=0),
        ).label('companies_with_roa'),
    ]


class CompanyRepository(BaseRepository[CompanyDataORM]):
    """Репозиторий компаний с методами агрегации."""

    async def aggregate_by(
        self,
        session: AsyncSession,
        group_key: str,
    ) -> list[dict]:
        """GROUP BY group_key, суммирует финансовые показатели.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            group_key: Поле модели для группировки (subject/district/industry).

        Returns:
            Список словарей {group_key: str, field: float, ...}.
        """
        group_col = getattr(CompanyDataORM, group_key)
        rows = await session.execute(
            select(
                group_col,
                func.sum(CompanyDataORM.current_business_value).label(
                    'current_business_value',
                ),
                func.sum(CompanyDataORM.liquidation_value).label(
                    'liquidation_value',
                ),
                func.sum(CompanyDataORM.creditor_return_rate).label(
                    'creditor_return_rate',
                ),
                func.sum(CompanyDataORM.working_capital_need).label(
                    'working_capital_need',
                ),
                func.sum(CompanyDataORM.profit_before_tax).label(
                    'profit_before_tax',
                ),
            ).group_by(group_col),
        )
        return [dict(row._mapping) for row in rows]  # noqa: WPS437

    async def compute_common_info(
        self,
        session: AsyncSession,
        group_key: str,
    ) -> list[dict]:
        """GROUP BY group_key, считает счётчики для CommonInfo-таблицы.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            group_key: Поле модели для группировки (subject/district/industry).

        Returns:
            Список словарей со счётчиками по каждой группе.
        """
        group_col = getattr(CompanyDataORM, group_key)
        no_debt = and_(
            func.coalesce(CompanyDataORM.tax_debt, 0) == 0,
            func.coalesce(CompanyDataORM.enforcement_debt, 0) == 0,
        )
        columns = _common_info_columns(group_col, no_debt)
        rows = await session.execute(
            select(*columns).group_by(group_col),
        )
        return [dict(row._mapping) for row in rows]  # noqa: WPS437


company_repository = CompanyRepository(CompanyDataORM)
