"""Pydantic схемы для данных регионов."""

from pydantic import BaseModel


class RegionDataSchema(BaseModel):
    """Схема агрегированных финансовых данных по региону."""

    id: int
    subject: str
    current_business_value: float | None
    liquidation_value: float | None
    creditor_return_rate: float | None
    working_capital_need: float | None
    profit_before_tax: float | None

    model_config = {'from_attributes': True}


class RegionAvgSchema(BaseModel):
    """Среднее значение показателей для одной компании в регионе."""

    region_name: str
    total_companies: int
    avg_current_business_value: float | None
    avg_liquidation_value: float | None
    avg_creditor_return_rate: float | None
    avg_working_capital_need: float | None
    avg_profit_before_tax: float | None


class RegionUpdateSchema(BaseModel):
    """Схема частичного обновления записи региона."""

    subject: str | None = None
    current_business_value: float | None = None
    liquidation_value: float | None = None
    creditor_return_rate: float | None = None
    working_capital_need: float | None = None
    profit_before_tax: float | None = None
