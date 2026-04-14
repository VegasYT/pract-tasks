"""Бизнес-логика загрузки данных компаний из CSV."""

import io

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.company import company_repository as company_repo
from app.repositories.county import county_repository as county_repo
from app.repositories.region import region_repository as region_repo

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
        group_key: Имя поля для группировки ('subject' или 'district').

    Returns:
        Список агрегированных записей с суммами по каждой группе.
    """
    data_frame = pd.DataFrame(records)
    grouped = data_frame.groupby(group_key)[list(_AGR_FIELDS)].sum()
    return grouped.reset_index().to_dict(orient='records')


async def _save_aggregates(
    session: AsyncSession,
    records: list[dict],
) -> None:
    """Сохраняет агрегированные данные в таблицы субъектов и округов.

    Args:
        session: Асинхронная сессия SQLAlchemy.
        records: Список словарей с данными компаний.
    """
    region_records = _aggregate_records(records, 'subject')
    await region_repo.clear_table(session)
    await region_repo.bulk_insert(session, region_records)

    county_records = _aggregate_records(records, 'district')
    await county_repo.clear_table(session)
    await county_repo.bulk_insert(session, county_records)


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
