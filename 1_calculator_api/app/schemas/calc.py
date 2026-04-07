"""Схемы данных для калькулятора."""
from pydantic import BaseModel


class CalcQueryParams(BaseModel):
    """Входные параметры запроса."""

    first: float
    second: float


class CalcResponse(BaseModel):
    """Ответ с результатом вычисления."""

    total: float
