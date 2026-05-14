"""Репозиторий для таблиц region_data и common_info_region."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import CommonInfoRegion, RegionDataORM
from app.repositories.base import BaseRepository


class RegionRepository(BaseRepository[RegionDataORM]):
    """Репозиторий region_data с методами получения, удаления и обновления."""

    async def get_by_id(
        self,
        session: AsyncSession,
        region_id: int,
    ) -> RegionDataORM | None:
        """Возвращает запись по id или None."""
        return (
            await session.execute(
                select(RegionDataORM).where(RegionDataORM.id == region_id),
            )
        ).scalar_one_or_none()

    async def delete_by_id(
        self,
        session: AsyncSession,
        region_id: int,
    ) -> bool:
        """Удаляет запись и связанный CommonInfoRegion по id.

        Returns:
            True если запись найдена и удалена, False если не найдена.
        """
        exists = await self.get_by_id(session, region_id)
        if exists is None:
            return False
        await session.execute(
            delete(CommonInfoRegion).where(
                CommonInfoRegion.region_id == region_id,
            ),
        )
        await session.execute(
            delete(RegionDataORM).where(RegionDataORM.id == region_id),
        )
        return True

    async def update_by_id(
        self,
        session: AsyncSession,
        region_id: int,
        fields: dict,
    ) -> RegionDataORM | None:
        """Частично обновляет запись по id.

        Returns:
            Обновлённую запись или None если не найдена.
        """
        record = await self.get_by_id(session, region_id)
        if record is None:
            return None
        for field, field_val in fields.items():
            setattr(record, field, field_val)
        await session.flush()
        return record

    async def get_avg_by_region_name(
        self,
        session: AsyncSession,
        region_name: str,
    ) -> tuple | None:
        """JOIN region_data + common_info_region по названию субъекта.

        Returns:
            Кортеж (RegionDataORM, CommonInfoRegion) или None если не найдено.
        """
        join_cond = CommonInfoRegion.region_id == RegionDataORM.id
        stmt = select(RegionDataORM, CommonInfoRegion).join(
            CommonInfoRegion, join_cond,
        ).where(RegionDataORM.subject == region_name)
        return (await session.execute(stmt)).first()


region_repository = RegionRepository(RegionDataORM)
common_info_region_repository = BaseRepository(CommonInfoRegion)
