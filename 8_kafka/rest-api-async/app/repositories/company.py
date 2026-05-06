"""Репозиторий для работы с таблицей CompanyDataORM."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import CompanyDataORM
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[CompanyDataORM]):
    """Репозиторий компаний с поддержкой пагинации и фильтрации."""

    async def get_paginated(  # noqa: WPS210
        self,
        session: AsyncSession,
        page: int,
        page_size: int,
        region_name: str | None = None,
    ) -> tuple[list[CompanyDataORM], int]:
        """Возвращает страницу записей и общее количество.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            page: Номер страницы (с 1).
            page_size: Размер страницы.
            region_name: Фильтр по субъекту РФ (опционально).

        Returns:
            Кортеж (список записей, общее количество).
        """
        stmt = select(CompanyDataORM)
        count_stmt = select(func.count()).select_from(CompanyDataORM)

        if region_name is not None:
            stmt = stmt.where(CompanyDataORM.subject == region_name)
            count_stmt = count_stmt.where(
                CompanyDataORM.subject == region_name,
            )

        total = (await session.execute(count_stmt)).scalar_one()
        offset = (page - 1) * page_size
        rows = (
            await session.execute(stmt.offset(offset).limit(page_size))
        ).scalars().all()

        return rows, total


company_repository = CompanyRepository(CompanyDataORM)
