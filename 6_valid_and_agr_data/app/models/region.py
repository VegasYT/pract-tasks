"""ORM модель агрегированных данных по субъектам РФ."""

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RegionDataORM(Base):
    """Агрегированные показатели компаний в разрезе субъекта РФ."""

    __tablename__ = 'region_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    current_business_value: Mapped[float] = mapped_column(
        Float, nullable=True,
    )
    liquidation_value: Mapped[float] = mapped_column(Float, nullable=True)
    creditor_return_rate: Mapped[float] = mapped_column(Float, nullable=True)
    working_capital_need: Mapped[float] = mapped_column(Float, nullable=True)
    profit_before_tax: Mapped[float] = mapped_column(Float, nullable=True)
