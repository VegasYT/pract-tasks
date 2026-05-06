"""ORM модели агрегированных данных по федеральным округам."""

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CountyDataORM(Base):
    """Агрегированные показатели компаний в разрезе федерального округа."""

    __tablename__ = 'county_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district: Mapped[str] = mapped_column(String, nullable=False)
    current_business_value: Mapped[float] = mapped_column(
        Float, nullable=True,
    )
    liquidation_value: Mapped[float] = mapped_column(Float, nullable=True)
    creditor_return_rate: Mapped[float] = mapped_column(Float, nullable=True)
    working_capital_need: Mapped[float] = mapped_column(Float, nullable=True)
    profit_before_tax: Mapped[float] = mapped_column(Float, nullable=True)


class CommonInfoCounty(Base):
    """Агрегированные счётчики компаний в разрезе федерального округа."""

    __tablename__ = 'common_info_county'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    county_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('county_data.id'), nullable=False, unique=True,
    )
    district: Mapped[str] = mapped_column(String, nullable=False)

    # Всего компаний по округу
    total_companies: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    # Компании со стоимостью бизнеса > 0
    companies_with_business_value: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    # Компании с прибылью (profit_before_tax > 0)
    companies_with_profit: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    # Компании без задолженностей (tax_debt == 0 и enforcement_debt == 0)
    companies_without_debt: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    # Компании с рангом платёжеспособности > 0
    companies_with_solvency_rank: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    # Компании с коэффициентом рентабельности активов != 0
    companies_with_roa: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )

    county = relationship('CountyDataORM', backref='common_info')
