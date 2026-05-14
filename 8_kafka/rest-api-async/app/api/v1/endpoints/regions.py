"""Эндпоинты для работы с данными регионов."""

import logging

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user, current_superuser
from app.db.session import get_db
from app.models.user import User
from app.schemas.region import RegionUpdateSchema
from app.schemas.upload import ErrorResponseSchema
from app.services import region as region_service
from app.services.region import RegionNotFoundError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get('/regions/avg', status_code=status.HTTP_200_OK)
async def get_region_avg(
    region_name: str = Query(..., description='Название субъекта РФ'),
    session: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
) -> JSONResponse:
    """Возвращает среднее значение показателей для одной компании в регионе."""
    logger.info('get region avg: region_name=%s', region_name)
    try:
        response = await region_service.get_region_avg(session, region_name)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.model_dump(),
        )
    except RegionNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponseSchema(
                detail='region "{0}" not found'.format(region_name),
            ).model_dump(),
        )
    except Exception as exc:
        logger.error('failed to get region avg for "%s": %s', region_name, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseSchema(detail=str(exc)).model_dump(),
        )


@router.delete('/regions/{region_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_region(
    region_id: int,
    session: AsyncSession = Depends(get_db),
    _user: User = Depends(current_active_user),
) -> JSONResponse:
    """Удаляет запись региона и связанный CommonInfoRegion по id."""
    logger.info('delete region: id=%d', region_id)
    try:
        await region_service.delete_region(session, region_id)
    except RegionNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponseSchema(
                detail='region {0} not found'.format(region_id),
            ).model_dump(),
        )
    except Exception as exc:
        logger.error('failed to delete region %d: %s', region_id, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseSchema(detail=str(exc)).model_dump(),
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch('/regions/{region_id}', status_code=status.HTTP_200_OK)
async def patch_region(
    region_id: int,
    body: RegionUpdateSchema,
    session: AsyncSession = Depends(get_db),
    _user: User = Depends(current_active_user),
) -> JSONResponse:
    """Частично обновляет запись региона по id."""
    logger.info('patch region: id=%d', region_id)
    fields = body.model_dump(exclude_unset=True)
    if not fields:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponseSchema(
                detail='no fields to update',
            ).model_dump(),
        )
    try:
        response = await region_service.patch_region(
            session, region_id, fields,
        )
    except RegionNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponseSchema(
                detail='region {0} not found'.format(region_id),
            ).model_dump(),
        )
    except Exception as exc:
        logger.error('failed to patch region %d: %s', region_id, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseSchema(detail=str(exc)).model_dump(),
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(),
    )
