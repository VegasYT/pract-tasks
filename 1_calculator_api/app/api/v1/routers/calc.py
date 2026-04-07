"""Роутер для операций калькулятора."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.calc import CalcQueryParams, CalcResponse
from app.services import calc

router = APIRouter(prefix='/calc', tags=['Операции'])


@router.get('/sum', response_model=CalcResponse, summary='Сложение')
def sum_numbers(
    query: Annotated[CalcQueryParams, Depends()],
) -> CalcResponse:
    """Сложить два числа.

    Args:
        query: параметры запроса с двумя числами.

    Returns:
        Результат сложения.
    """
    return CalcResponse(total=calc.add(query.first, query.second))


@router.get('/multiply', response_model=CalcResponse, summary='Умножение')
def multiply_numbers(
    query: Annotated[CalcQueryParams, Depends()],
) -> CalcResponse:
    """Умножить два числа.

    Args:
        query: параметры запроса с двумя числами.

    Returns:
        Результат умножения.
    """
    return CalcResponse(total=calc.multiply(query.first, query.second))


@router.get(
    '/divide',
    response_model=CalcResponse,
    summary='Деление',
    responses={400: {'description': 'Деление на ноль'}},
)
def divide_numbers(
    query: Annotated[CalcQueryParams, Depends()],
) -> CalcResponse:
    """Разделить первое число на второе.

    Args:
        query: параметры запроса с двумя числами.

    Returns:
        Результат деления.
    """
    return CalcResponse(total=calc.divide(query.first, query.second))
