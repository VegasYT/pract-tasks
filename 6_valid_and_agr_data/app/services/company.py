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

# Поля для агрегации (сумма по группе)
_AGR_FIELDS = (  # noqa: WPS407
    'current_business_value',
    'liquidation_value',
    'creditor_return_rate',
    'working_capital_need',
    'profit_before_tax',
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


def _aggregate_records(
    records: list[dict],
    group_key: str,
) -> list[dict]:
    """Агрегирует записи по заданному полю, суммируя финансовые показатели.

    Args:
        records: Список словарей с данными компаний.
        group_key: Имя поля для группировки.

    Returns:
        Список агрегированных записей с суммами по каждой группе.
    """
    data_frame = pd.DataFrame(records)
    grouped = data_frame.groupby(group_key)[list(_AGR_FIELDS)].sum()
    return grouped.reset_index().to_dict(orient='records')


def _build_common_info_row(
    group_key: str,
    group_val: str,
    group_df: pd.DataFrame,
) -> dict:
    """Строит словарь счётчиков для одной группы CommonInfo."""
    no_tax = group_df['tax_debt'].fillna(0) == 0
    no_enforcement = group_df['enforcement_debt'].fillna(0) == 0
    return {
        group_key: group_val,
        'total_companies': len(group_df),
        'companies_with_business_value': int(
            (group_df['current_business_value'].fillna(0) > 0).sum(),
        ),
        'companies_with_profit': int(
            (group_df['profit_before_tax'].fillna(0) > 0).sum(),
        ),
        'companies_without_debt': int(
            (no_tax & no_enforcement).sum(),  # noqa: WPS465
        ),
        'companies_with_solvency_rank': int(
            (group_df['solvency_rank'].fillna(0) > 0).sum(),
        ),
        'companies_with_roa': int(
            (group_df['creditor_return_rate'].fillna(0) != 0).sum(),
        ),
    }


def _compute_common_info(
    records: list[dict],
    group_key: str,
) -> list[dict]:
    """Вычисляет счётчики компаний для CommonInfo-таблицы.

    Args:
        records: Список словарей с данными компаний.
        group_key: Поле для группировки.

    Returns:
        Список словарей с агрегированными счётчиками.
    """
    data_frame = pd.DataFrame(records)
    return [
        _build_common_info_row(group_key, group_val, group_df)
        for group_val, group_df in data_frame.groupby(group_key)
    ]


async def _save_region_aggregates(  # noqa: WPS217
    session: AsyncSession,
    records: list[dict],
) -> None:
    """Сохраняет агрегаты и CommonInfo по субъектам РФ."""
    await region_repo.clear_table(session)
    await region_repo.bulk_insert(
        session, _aggregate_records(records, _KEY_SUBJECT),
    )
    await session.flush()

    region_rows = await region_repo.get_all(session)
    region_id_map = {region.subject: region.id for region in region_rows}

    common_rows = _compute_common_info(records, _KEY_SUBJECT)
    for common_row in common_rows:
        common_row['region_id'] = region_id_map.get(common_row[_KEY_SUBJECT])
    await common_info_region_repo.clear_table(session)
    await common_info_region_repo.bulk_insert(session, common_rows)


async def _save_county_aggregates(  # noqa: WPS217
    session: AsyncSession,
    records: list[dict],
) -> None:
    """Сохраняет агрегаты и CommonInfo по федеральным округам."""
    await county_repo.clear_table(session)
    await county_repo.bulk_insert(
        session, _aggregate_records(records, _KEY_DISTRICT),
    )
    await session.flush()

    county_rows = await county_repo.get_all(session)
    county_id_map = {county.district: county.id for county in county_rows}

    common_rows = _compute_common_info(records, _KEY_DISTRICT)
    for common_row in common_rows:
        common_row['county_id'] = county_id_map.get(common_row[_KEY_DISTRICT])
    await common_info_county_repo.clear_table(session)
    await common_info_county_repo.bulk_insert(session, common_rows)


async def _save_industry_aggregates(  # noqa: WPS217
    session: AsyncSession,
    records: list[dict],
) -> None:
    """Сохраняет агрегаты и CommonInfo по отраслям."""
    await industry_repo.clear_table(session)
    await industry_repo.bulk_insert(
        session, _aggregate_records(records, _KEY_INDUSTRY),
    )
    await session.flush()

    industry_rows = await industry_repo.get_all(session)
    industry_id_map = {ind.industry: ind.id for ind in industry_rows}

    common_rows = _compute_common_info(records, _KEY_INDUSTRY)
    for common_row in common_rows:
        common_row['industry_id'] = industry_id_map.get(
            common_row[_KEY_INDUSTRY],
        )
    await common_info_industry_repo.clear_table(session)
    await common_info_industry_repo.bulk_insert(session, common_rows)


async def _save_aggregates(
    session: AsyncSession,
    records: list[dict],
) -> None:
    """Сохраняет агрегированные данные по регионам, округам и отраслям.

    Args:
        session: Асинхронная сессия SQLAlchemy.
        records: Список словарей с данными компаний.
    """
    await _save_region_aggregates(session, records)
    await _save_county_aggregates(session, records)
    await _save_industry_aggregates(session, records)


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
    await _save_aggregates(session, records)
    await session.commit()
    return len(records)
