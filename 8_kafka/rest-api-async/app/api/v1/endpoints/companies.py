"""Эндпоинты для работы с данными компаний."""

import logging

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.upload import ErrorResponseSchema
from app.services import company as company_service

router = APIRouter()
logger = logging.getLogger(__name__)

_DEFAULT_PAGE_SIZE = 20


@router.get('/companies', status_code=status.HTTP_200_OK)
async def get_companies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=_DEFAULT_PAGE_SIZE, ge=1, le=100),
    region_name: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    _user: User = Depends(current_active_user),
) -> JSONResponse:
    """Возвращает пагинированный список компаний с фильтрацией по региону."""
    logger.info(
        'get companies: page=%d, page_size=%d, region_name=%s',
        page,
        page_size,
        region_name,
    )
    try:
        response = await company_service.get_companies_page(
            session, page, page_size, region_name,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.model_dump(),
        )
    except Exception as exc:
        logger.error('failed to get companies: %s', exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseSchema(detail=str(exc)).model_dump(),
        )
