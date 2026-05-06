"""ORM модель компании."""

from sqlalchemy import JSON, BigInteger, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CompanyDataORM(Base):
    """Таблица с данными компаний и признаками банкротства."""

    __tablename__ = 'company_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inn: Mapped[int] = mapped_column(BigInteger, nullable=True)
    okved: Mapped[str] = mapped_column(String, nullable=True)
    okved_description: Mapped[str] = mapped_column(Text, nullable=True)
    industry: Mapped[str] = mapped_column(Text, nullable=True)
    subject: Mapped[str] = mapped_column(String, nullable=True)
    district: Mapped[str] = mapped_column(String, nullable=True)
    current_business_value: Mapped[float] = mapped_column(
        Float, nullable=True,
    )
    liquidation_value: Mapped[float] = mapped_column(Float, nullable=True)
    creditor_return_rate: Mapped[float] = mapped_column(Float, nullable=True)
    working_capital_need: Mapped[float] = mapped_column(Float, nullable=True)
    profit_before_tax: Mapped[float] = mapped_column(Float, nullable=True)
    tax_debt: Mapped[float] = mapped_column(Float, nullable=True)
    enforcement_debt: Mapped[float] = mapped_column(Float, nullable=True)
    guarantee_limit: Mapped[str] = mapped_column(String, nullable=True)
    solvency_rank: Mapped[float] = mapped_column(Float, nullable=True)
    organization_age: Mapped[float] = mapped_column(Float, nullable=True)

    bankruptcy_data: Mapped[dict] = mapped_column(JSON, nullable=True)
