"""Сервис для работы с данными компаний."""

import math
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.company import company_repository as company_repo
from app.schemas.company import CompanySchema, PaginatedCompaniesSchema

logger = logging.getLogger(__name__)


async def get_companies_page(
    session: AsyncSession,
    page: int,
    page_size: int,
    region_name: str | None,
) -> PaginatedCompaniesSchema:
    """Возвращает пагинированный список компаний.

    Args:
        session: Сессия БД.
        page: Номер страницы (с 1).
        page_size: Размер страницы.
        region_name: Фильтр по субъекту РФ.

    Returns:
        Схема с данными страницы и метаинформацией.
    """
    rows, total = await company_repo.get_paginated(
        session, page, page_size, region_name,
    )
    return PaginatedCompaniesSchema(
        companies=[CompanySchema.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )
