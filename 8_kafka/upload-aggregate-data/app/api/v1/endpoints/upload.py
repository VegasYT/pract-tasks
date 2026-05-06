"""Эндпоинт загрузки CSV с данными компаний."""

import logging

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.company import ErrorResponseSchema, UploadResponseSchema
from app.services import company as company_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/upload', status_code=status.HTTP_201_CREATED)
async def upload_csv(
    csv_file: UploadFile,
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Принимает CSV файл и загружает данные в БД."""
    logger.info('upload request received, file: %s', csv_file.filename)
    try:
        file_bytes = await csv_file.read()
        rows_loaded = await company_service.load_companies(session, file_bytes)
        logger.info('upload complete, rows loaded: %d', rows_loaded)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=UploadResponseSchema(
                rows_loaded=rows_loaded,
            ).model_dump(),
        )
    except Exception as exc:
        logger.error('upload failed: %s', exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseSchema(detail=str(exc)).model_dump(),
        )
