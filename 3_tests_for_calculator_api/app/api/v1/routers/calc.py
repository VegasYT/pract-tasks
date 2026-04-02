from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.calc import CalcQueryParams, CalcResponse
from app.services import calc

router = APIRouter(prefix="/calc", tags=["Операции"])


@router.get("/sum", response_model=CalcResponse, summary="Сложение")
def sum_numbers(params: Annotated[CalcQueryParams, Depends()]) -> CalcResponse:
    return CalcResponse(result=calc.add(params.a, params.b))


@router.get("/multiply", response_model=CalcResponse, summary="Умножение")
def multiply_numbers(params: Annotated[CalcQueryParams, Depends()]) -> CalcResponse:
    return CalcResponse(result=calc.multiply(params.a, params.b))


@router.get(
    "/divide",
    response_model=CalcResponse,
    summary="Деление",
    responses={400: {"description": "Деление на ноль"}},
)
def divide_numbers(params: Annotated[CalcQueryParams, Depends()]) -> CalcResponse:
    return CalcResponse(result=calc.divide(params.a, params.b))
