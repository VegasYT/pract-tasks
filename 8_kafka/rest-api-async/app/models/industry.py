"""ORM модели агрегированных данных по отраслям."""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IndustryDataORM(Base):
    """Агрегированные показатели компаний в разрезе отрасли."""

    __tablename__ = 'industry_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    industry: Mapped[str] = mapped_column(Text, nullable=False)
    current_business_value: Mapped[float] = mapped_column(Float, nullable=True)
    liquidation_value: Mapped[float] = mapped_column(Float, nullable=True)
    creditor_return_rate: Mapped[float] = mapped_column(Float, nullable=True)
    working_capital_need: Mapped[float] = mapped_column(Float, nullable=True)
    profit_before_tax: Mapped[float] = mapped_column(Float, nullable=True)


class CommonInfoIndustry(Base):
    """Агрегированные счётчики компаний в разрезе отрасли."""

    __tablename__ = 'common_info_industry'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    industry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('industry_data.id'), nullable=False, unique=True,
    )
    industry: Mapped[str] = mapped_column(Text, nullable=False)

    total_companies: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    companies_with_business_value: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    companies_with_profit: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    companies_without_debt: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    companies_with_solvency_rank: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    companies_with_roa: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )

    industry_ref = relationship('IndustryDataORM', backref='common_info')
