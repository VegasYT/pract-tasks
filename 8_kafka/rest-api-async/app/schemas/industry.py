"""Pydantic схемы для данных по отраслям."""

from pydantic import BaseModel


class IndustryPercentSchema(BaseModel):
    """Процентные значения компаний отрасли от общего числа по выбранным."""

    industry_id: int
    industry_name: str
    total_companies: float | None
    companies_with_business_value: float | None
    companies_with_profit: float | None
    companies_without_debt: float | None
    companies_with_solvency_rank: float | None
    companies_with_roa: float | None
