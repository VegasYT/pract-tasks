"""Сервис постановки CSV-файла в очередь Kafka."""

import base64
import logging

from fastapi import UploadFile

from app.kafka.producer import send_upload_message
from app.schemas.upload import (
    ALLOWED_CONTENT_TYPES,
    MAX_FILE_SIZE_BYTES,
    UploadAcceptedSchema,
)

logger = logging.getLogger(__name__)


class InvalidFileError(Exception):
    """Файл не прошёл валидацию."""


class FileTooLargeError(Exception):
    """Файл превышает допустимый размер."""


async def enqueue_csv(csv_file: UploadFile) -> UploadAcceptedSchema:
    """Валидирует файл и отправляет его в Kafka.

    Args:
        csv_file: Загруженный файл.

    Returns:
        Схема с подтверждением постановки в очередь.

    Raises:
        InvalidFileError: Неверный content-type.
        FileTooLargeError: Файл превышает лимит.
    """
    if csv_file.content_type not in ALLOWED_CONTENT_TYPES:
        raise InvalidFileError(
            'invalid content type: {0}'.format(csv_file.content_type),
        )

    file_bytes = await csv_file.read()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(
            'file too large, max {0} bytes'.format(MAX_FILE_SIZE_BYTES),
        )

    filename = csv_file.filename or 'upload.csv'
    content_b64 = base64.b64encode(file_bytes).decode('utf-8')

    await send_upload_message(filename, content_b64)
    logger.info('file queued: %s', filename)

    return UploadAcceptedSchema(
        message='file {0} accepted for processing'.format(filename),
    )
