"""Сервис для работы с данными регионов."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.region import region_repository as region_repo
from app.schemas.region import RegionAvgSchema, RegionDataSchema

logger = logging.getLogger(__name__)


class RegionNotFoundError(Exception):
    """Регион с указанным id не найден."""


async def delete_region(session: AsyncSession, region_id: int) -> None:
    """Удаляет регион и связанный CommonInfoRegion.

    Raises:
        RegionNotFoundError: Если регион не найден.
    """
    deleted = await region_repo.delete_by_id(session, region_id)
    if not deleted:
        raise RegionNotFoundError(region_id)
    await session.commit()
    logger.info('region %d deleted', region_id)


async def patch_region(
    session: AsyncSession,
    region_id: int,
    fields: dict,
) -> RegionDataSchema:
    """Частично обновляет регион.

    Raises:
        RegionNotFoundError: Если регион не найден.
    """
    record = await region_repo.update_by_id(session, region_id, fields)
    if record is None:
        raise RegionNotFoundError(region_id)
    await session.commit()
    logger.info('region %d updated', region_id)
    return RegionDataSchema.model_validate(record)


def _safe_div(amount: float | None, count: int) -> float | None:
    """Делит amount на count.

    Возвращает None если amount равен None или count == 0.
    """
    if amount is None or count == 0:
        return None
    return amount / count


async def get_region_avg(
    session: AsyncSession,
    region_name: str,
) -> RegionAvgSchema:
    """Возвращает среднее значение показателей для одной компании в регионе.

    Raises:
        RegionNotFoundError: Если регион не найден.
    """
    row = await region_repo.get_avg_by_region_name(session, region_name)
    if row is None:
        raise RegionNotFoundError(region_name)

    region_data, common_info = row
    count = common_info.total_companies

    logger.info('region avg fetched: %s, companies=%d', region_name, count)

    return RegionAvgSchema(
        region_name=region_data.subject,
        total_companies=count,
        avg_current_business_value=_safe_div(
            region_data.current_business_value, count,
        ),
        avg_liquidation_value=_safe_div(
            region_data.liquidation_value, count,
        ),
        avg_creditor_return_rate=_safe_div(
            region_data.creditor_return_rate, count,
        ),
        avg_working_capital_need=_safe_div(
            region_data.working_capital_need, count,
        ),
        avg_profit_before_tax=_safe_div(
            region_data.profit_before_tax, count,
        ),
    )
