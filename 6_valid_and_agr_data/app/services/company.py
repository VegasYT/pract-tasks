"""Бизнес-логика загрузки данных компаний из CSV."""

import io

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.company import company_repository as company_repo
from app.repositories.county import (
    common_info_county_repository as common_info_county_repo,
    county_repository as county_repo,
)
from app.repositories.industry import (
    common_info_industry_repository as common_info_industry_repo,
    industry_repository as industry_repo,
)
from app.repositories.region import (
    common_info_region_repository as common_info_region_repo,
    region_repository as region_repo,
)

# Граничный столбец: начиная с него все поля уходят в bankruptcy_data
_BANKRUPTCY_COLUMN = (
    'возбуждено производство по делу о несостоятельности (банкротстве)'
)

# Маппинг CSV-столбцов на поля ORM (до границы)
_COLUMN_MAP = {  # noqa: WPS407
    'ID': 'inn',
    'оквэд': 'okved',
    'расшифровка оквэд': 'okved_description',
    'Отрасль': 'industry',
    'Субъект': 'subject',
    'Округ': 'district',
    'текущая стоимость бизнеса': 'current_business_value',
    'ликвидационная стоимость бизнеса': 'liquidation_value',
    'расчёт возвратности средств для кредиторов': 'creditor_return_rate',
    'потребность в оборотных средствах': 'working_capital_need',
    'прибыль до налогообложения': 'profit_before_tax',
    'задолженность по налогам': 'tax_debt',
    'исполнительное производство без учета налогов': 'enforcement_debt',
    'Лимит поручительства': 'guarantee_limit',
    'ранг платёжеспособности': 'solvency_rank',
    'возраст организации': 'organization_age',
}

# Ключи группировки - вынесены, чтобы избежать WPS226 (over-use string literal)
_KEY_SUBJECT = 'subject'  # noqa: WPS226
_KEY_DISTRICT = 'district'  # noqa: WPS226
_KEY_INDUSTRY = 'industry'  # noqa: WPS226


def _build_record(
    row: pd.Series,
    main_cols: list,
    json_cols: list,
) -> dict:
    """Строит словарь записи из строки датафрейма."""
    record = {
        _COLUMN_MAP[col]: row[col]
        for col in main_cols
        if col in _COLUMN_MAP
    }
    record['bankruptcy_data'] = {col: row[col] for col in json_cols}
    return record


def _split_columns(all_columns: list) -> tuple[list, list]:
    """Разделяет столбцы на основные и JSON-группу."""
    boundary = all_columns.index(_BANKRUPTCY_COLUMN)
    return all_columns[:boundary], all_columns[boundary:]


def _parse_csv(file_bytes: bytes) -> list[dict]:
    """Парсит CSV и возвращает список записей для вставки в БД."""
    data_frame = pd.read_csv(io.BytesIO(file_bytes), index_col=0)
    main_columns, json_columns = _split_columns(list(data_frame.columns))
    return [
        _build_record(row, main_columns, json_columns)
        for _, row in data_frame.iterrows()
    ]


async def _save_region_aggregates(  # noqa: WPS217
    session: AsyncSession,
) -> None:
    """Сохраняет агрегаты и CommonInfo по субъектам РФ."""
    await common_info_region_repo.clear_table(session)
    await region_repo.clear_table(session)
    await region_repo.bulk_insert(
        session,
        await company_repo.aggregate_by(session, _KEY_SUBJECT),
    )
    await session.flush()

    common_rows = await common_info_region_repo.compute_from_companies(session)
    await common_info_region_repo.bulk_insert(session, common_rows)


async def _save_county_aggregates(  # noqa: WPS217
    session: AsyncSession,
) -> None:
    """Сохраняет агрегаты и CommonInfo по федеральным округам."""
    await common_info_county_repo.clear_table(session)
    await county_repo.clear_table(session)
    await county_repo.bulk_insert(
        session,
        await company_repo.aggregate_by(session, _KEY_DISTRICT),
    )
    await session.flush()

    common_rows = await common_info_county_repo.compute_from_companies(session)
    await common_info_county_repo.bulk_insert(session, common_rows)


async def _save_industry_aggregates(  # noqa: WPS217
    session: AsyncSession,
) -> None:
    """Сохраняет агрегаты и CommonInfo по отраслям."""
    await common_info_industry_repo.clear_table(session)
    await industry_repo.clear_table(session)
    await industry_repo.bulk_insert(
        session,
        await company_repo.aggregate_by(session, _KEY_INDUSTRY),
    )
    await session.flush()

    common_rows = await common_info_industry_repo.compute_from_companies(
        session,
    )
    await common_info_industry_repo.bulk_insert(session, common_rows)


async def _save_aggregates(session: AsyncSession) -> None:
    """Сохраняет агрегированные данные по регионам, округам и отраслям."""
    await _save_region_aggregates(session)
    await _save_county_aggregates(session)
    await _save_industry_aggregates(session)


async def load_companies(
    session: AsyncSession,
    file_bytes: bytes,
) -> int:
    """Очищает таблицы и загружает данные из CSV с агрегацией.

    Args:
        session: Асинхронная сессия SQLAlchemy.
        file_bytes: Содержимое CSV-файла в байтах.

    Returns:
        Количество загруженных строк основной таблицы.
    """
    records = _parse_csv(file_bytes)

    # Сначала фиксируем основные данные
    await company_repo.clear_table(session)
    await company_repo.bulk_insert(session, records)
    await session.commit()

    # Затем считаем и фиксируем агрегаты
    await _save_aggregates(session)
    await session.commit()
    return len(records)
