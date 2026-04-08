"""Бизнес-логика загрузки данных компаний из CSV."""

import io

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import company as company_repo

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


async def load_companies(
    session: AsyncSession,
    file_bytes: bytes,
) -> int:
    """Очищает таблицу и загружает данные из CSV. Возвращает кол-во строк."""
    records = _parse_csv(file_bytes)
    await company_repo.clear_table(session)
    await company_repo.bulk_insert(session, records)
    await session.commit()
    return len(records)
