"""Pydantic схемы для данных компании."""

from pydantic import BaseModel


class CompanySchema(BaseModel):
    """Схема записи компании для API-ответа."""

    id: int
    inn: int | None
    okved: str | None
    okved_description: str | None
    industry: str | None
    subject: str | None
    district: str | None
    current_business_value: float | None
    liquidation_value: float | None
    creditor_return_rate: float | None
    working_capital_need: float | None
    profit_before_tax: float | None
    tax_debt: float | None
    enforcement_debt: float | None
    guarantee_limit: str | None
    solvency_rank: float | None
    organization_age: float | None

    model_config = {'from_attributes': True}


class PaginatedCompaniesSchema(BaseModel):
    """Схема пагинированного списка компаний."""

    companies: list[CompanySchema]
    total: int
    page: int
    page_size: int
    pages: int
