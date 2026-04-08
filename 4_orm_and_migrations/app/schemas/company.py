"""Pydantic схемы для эндпоинта загрузки."""

from pydantic import BaseModel


class UploadResponseSchema(BaseModel):
    """Ответ при успешной загрузке CSV."""

    rows_loaded: int


class ErrorResponseSchema(BaseModel):
    """Ответ при ошибке."""

    detail: str
