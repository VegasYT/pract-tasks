"""Бизнес-логика калькулятора."""
from fastapi import HTTPException

_ROUND_PRECISION = 10
_HTTP_BAD_REQUEST = 400


def _round(number: float) -> float:
    # Срезаем погрешность float-арифметики (0.1 + 0.2 = 0.30000000000000004)
    return round(number, _ROUND_PRECISION)


def add(first: float, second: float) -> float:
    """Сложить два числа.

    Args:
        first: первое слагаемое.
        second: второе слагаемое.

    Returns:
        Сумма first и second.
    """
    return _round(first + second)


def multiply(first: float, second: float) -> float:
    """Умножить два числа.

    Args:
        first: множитель.
        second: множитель.

    Returns:
        Произведение first и second.
    """
    return _round(first * second)


def divide(first: float, second: float) -> float:
    """Разделить первое число на второе.

    Args:
        first: делимое.
        second: делитель.

    Returns:
        Частное first и second.

    Raises:
        HTTPException: если second равен нулю.
    """
    if second == 0:
        raise HTTPException(
            status_code=_HTTP_BAD_REQUEST,
            detail='Деление на ноль. Параметр b должен быть ненулевым.',
        )
    return _round(first / second)
