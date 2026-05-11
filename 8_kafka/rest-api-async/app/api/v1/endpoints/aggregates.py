"""Эндпоинты для получения агрегированных данных."""

import logging
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.upload import ErrorResponseSchema
from app.services import aggregates as aggregates_service

router = APIRouter()
logger = logging.getLogger(__name__)

GroupBy = Literal['region', 'county', 'industry']

_GROUP_REGION = 'region'  # noqa: WPS226


@router.get('/aggregates/financial', status_code=status.HTTP_200_OK)
async def get_financial_aggregates(
    group_by: GroupBy = Query(default=_GROUP_REGION),
    session: AsyncSession = Depends(get_db),
    _user: User = Depends(current_active_user),
) -> JSONResponse:
    """Возвращает финансовые суммы по регионам, округам или отраслям."""
    logger.info('get financial aggregates, group_by=%s', group_by)
    try:
        response = await aggregates_service.get_financial(session, group_by)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.model_dump(),
        )
    except Exception as exc:
        logger.error('failed to get financial aggregates: %s', exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseSchema(detail=str(exc)).model_dump(),
        )


@router.get('/aggregates/counts', status_code=status.HTTP_200_OK)
async def get_counts_aggregates(
    group_by: GroupBy = Query(default=_GROUP_REGION),
    session: AsyncSession = Depends(get_db),
    _user: User = Depends(current_active_user),
) -> JSONResponse:
    """Возвращает счётчики компаний по регионам, округам или отраслям."""
    logger.info('get counts aggregates, group_by=%s', group_by)
    try:
        response = await aggregates_service.get_counts(session, group_by)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.model_dump(),
        )
    except Exception as exc:
        logger.error('failed to get counts aggregates: %s', exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseSchema(detail=str(exc)).model_dump(),
        )
