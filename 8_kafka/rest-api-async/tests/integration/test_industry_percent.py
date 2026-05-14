"""Интеграционные тесты эндпоинта GET /aggregates/industry-percent."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.industry import CommonInfoIndustry, IndustryDataORM


async def _insert_industry(
    session: AsyncSession,
    industry_name: str,
    total: int,
    with_business: int,
    with_profit: int,
    without_debt: int,
    with_solvency: int,
    with_roa: int,
) -> CommonInfoIndustry:
    industry = IndustryDataORM(
        industry=industry_name,
        current_business_value=0.0,
        liquidation_value=0.0,
        creditor_return_rate=0.0,
        working_capital_need=0.0,
        profit_before_tax=0.0,
    )
    session.add(industry)
    await session.flush()

    info = CommonInfoIndustry(
        industry_id=industry.id,
        industry=industry_name,
        total_companies=total,
        companies_with_business_value=with_business,
        companies_with_profit=with_profit,
        companies_without_debt=without_debt,
        companies_with_solvency_rank=with_solvency,
        companies_with_roa=with_roa,
    )
    session.add(info)
    await session.commit()
    return info


@pytest.mark.asyncio
async def test_industry_percent_success(client: AsyncClient, db_session: AsyncSession):
    """Успешный запрос возвращает процентные значения для найденных отраслей."""
    info1 = await _insert_industry(db_session, 'Отрасль А', 40, 30, 20, 10, 15, 5)
    info2 = await _insert_industry(db_session, 'Отрасль Б', 60, 50, 30, 20, 25, 10)

    response = await client.get(
        '/api/v1/aggregates/industry-percent',
        params={'industry_ids': [info1.industry_id, info2.industry_id]},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

    names = {item['industry_name'] for item in data}
    assert names == {'Отрасль А', 'Отрасль Б'}

    # Всего компаний: 40 + 60 = 100. Отрасль А: 40/100 = 40%
    item_a = next(d for d in data if d['industry_name'] == 'Отрасль А')
    assert item_a['total_companies'] == pytest.approx(40.0)

    # Отрасль Б: 60/100 = 60%
    item_b = next(d for d in data if d['industry_name'] == 'Отрасль Б')
    assert item_b['total_companies'] == pytest.approx(60.0)


@pytest.mark.asyncio
async def test_industry_percent_nonexistent_ids_skipped(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """Несуществующие id в списке пропускаются, возвращаются только найденные."""
    info = await _insert_industry(db_session, 'Отрасль В', 10, 8, 5, 3, 4, 2)

    response = await client.get(
        '/api/v1/aggregates/industry-percent',
        params={'industry_ids': [info.industry_id, 99999]},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['industry_name'] == 'Отрасль В'


@pytest.mark.asyncio
async def test_industry_percent_all_nonexistent(client: AsyncClient):
    """Все id несуществующие - возвращается пустой список."""
    response = await client.get(
        '/api/v1/aggregates/industry-percent',
        params={'industry_ids': [99998, 99999]},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_industry_percent_missing_param(client: AsyncClient):
    """Запрос без industry_ids возвращает 422."""
    response = await client.get('/api/v1/aggregates/industry-percent')

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
