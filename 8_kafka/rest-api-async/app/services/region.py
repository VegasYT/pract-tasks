"""Сервис для работы с данными регионов."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.region import region_repository as region_repo
from app.schemas.region import RegionDataSchema

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
