"""Pydantic схемы для агрегированных данных."""

from pydantic import BaseModel


class AggregateFinancialListSchema(BaseModel):
    """Список финансовых агрегатов по группе."""

    group_by: str
    records: list[dict]


class AggregateCountsListSchema(BaseModel):
    """Список счётчиков компаний по группе."""

    group_by: str
    records: list[dict]
