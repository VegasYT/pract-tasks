"""Pydantic схемы для эндпоинта отправки CSV в Kafka."""

from pydantic import BaseModel

_MB = 1024 * 1024
_MAX_SIZE_MB = 50
MAX_FILE_SIZE_BYTES: int = _MAX_SIZE_MB * _MB

ALLOWED_CONTENT_TYPES: frozenset = frozenset((
    'text/csv',
    'application/csv',
    'application/octet-stream',
))


class UploadAcceptedSchema(BaseModel):
    """Ответ при успешной постановке задачи в очередь."""

    status: str = 'accepted'
    message: str


class ErrorResponseSchema(BaseModel):
    """Ответ при ошибке."""

    detail: str
