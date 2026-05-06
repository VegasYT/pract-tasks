"""Эндпоинт отправки CSV в Kafka для последующей загрузки в БД."""

import logging

from aiokafka.errors import KafkaError
from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.schemas.upload import ErrorResponseSchema, UploadAcceptedSchema
from app.services import upload as upload_service
from app.services.upload import FileTooLargeError, InvalidFileError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/upload', status_code=status.HTTP_202_ACCEPTED)
async def upload_csv(csv_file: UploadFile) -> JSONResponse:
    """Принимает CSV, валидирует и отправляет в Kafka для загрузки."""
    logger.info('upload request received, file: %s', csv_file.filename)
    try:
        response = await upload_service.enqueue_csv(csv_file)
    except InvalidFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        )
    except KafkaError as exc:
        logger.error('kafka unavailable: %s', exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponseSchema(
                detail='kafka unavailable, try again later',
            ).model_dump(),
        )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=UploadAcceptedSchema.model_validate(response).model_dump(),
    )
