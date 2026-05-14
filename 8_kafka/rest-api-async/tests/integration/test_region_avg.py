"""Интеграционные тесты эндпоинта GET /regions/avg."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import CommonInfoRegion, RegionDataORM


async def _insert_region(session: AsyncSession, subject: str) -> RegionDataORM:
    region = RegionDataORM(
        subject=subject,
        current_business_value=1000.0,
        liquidation_value=800.0,
        creditor_return_rate=500.0,
        working_capital_need=200.0,
        profit_before_tax=100.0,
    )
    session.add(region)
    await session.flush()

    info = CommonInfoRegion(
        region_id=region.id,
        subject=subject,
        total_companies=4,
        companies_with_business_value=3,
        companies_with_profit=2,
        companies_without_debt=1,
        companies_with_solvency_rank=2,
        companies_with_roa=1,
    )
    session.add(info)
    await session.commit()
    return region


@pytest.mark.asyncio
async def test_region_avg_success(client: AsyncClient, db_session: AsyncSession):
    """Успешный запрос возвращает средние значения и количество компаний."""
    await _insert_region(db_session, 'Тестовый регион')

    response = await client.get(
        '/api/v1/regions/avg',
        params={'region_name': 'Тестовый регион'},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['region_name'] == 'Тестовый регион'
    assert data['total_companies'] == 4
    assert data['avg_current_business_value'] == pytest.approx(250.0)
    assert data['avg_liquidation_value'] == pytest.approx(200.0)
    assert data['avg_creditor_return_rate'] == pytest.approx(125.0)
    assert data['avg_working_capital_need'] == pytest.approx(50.0)
    assert data['avg_profit_before_tax'] == pytest.approx(25.0)


@pytest.mark.asyncio
async def test_region_avg_not_found(client: AsyncClient):
    """Несуществующий регион возвращает 404."""
    response = await client.get(
        '/api/v1/regions/avg',
        params={'region_name': 'Нет такого региона'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'detail' in response.json()


@pytest.mark.asyncio
async def test_region_avg_missing_param(client: AsyncClient):
    """Запрос без region_name возвращает 422."""
    response = await client.get('/api/v1/regions/avg')

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
