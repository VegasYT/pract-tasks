from fastapi import HTTPException


def _round(value: float) -> float:
    # Срезаем погрешность float-арифметики (0.1 + 0.2 = 0.30000000000000004)
    return round(value, 10)


def add(a: float, b: float) -> float:
    return _round(a + b)


def multiply(a: float, b: float) -> float:
    return _round(a * b)


def divide(a: float, b: float) -> float:
    if b == 0:
        raise HTTPException(
            status_code=400,
            detail="Деление на ноль невозможно. Параметр 'b' должен быть ненулевым.",
        )
    return _round(a / b)
