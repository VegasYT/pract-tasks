"""Интеграционные тесты эндпоинта загрузки CSV."""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_csv_success(client: AsyncClient, sample_csv: bytes):
    """Успешная загрузка валидного CSV возвращает 201 и количество строк."""
    response = await client.post(
        '/api/v1/upload',
        files={'csv_file': ('data.csv', sample_csv, 'text/csv')},
    )
    print(response.json())  # noqa: T201, WPS421
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert response.json()['rows_loaded'] == 1


@pytest.mark.asyncio
async def test_upload_invalid_file(client: AsyncClient):
    """Загрузка невалидного файла возвращает 500 с описанием ошибки."""
    response = await client.post(
        '/api/v1/upload',
        files={'csv_file': ('data.csv', b'not a valid csv !!!', 'text/csv')},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'detail' in response.json()
