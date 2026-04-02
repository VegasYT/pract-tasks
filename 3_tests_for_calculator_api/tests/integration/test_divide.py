import pytest
from fastapi.testclient import TestClient


# (a, b, ожидаемый результат)
@pytest.mark.parametrize("a, b, expected", [
    (10, 2, 5),
    (-10, -2, 5),
    (10, -2, -5),
    (7, 1, 7),
    (-7, 1, -7),
])
def test_divide(client: TestClient, a: float, b: float, expected: float) -> None:
    response = client.get("/v1/calc/divide", params={"a": a, "b": b})

    assert response.status_code == 200
    assert response.json() == {"result": expected}


def test_divide_by_zero(client: TestClient) -> None:
    response = client.get("/v1/calc/divide", params={"a": 10, "b": 0})

    assert response.status_code == 400
    # Проверяем, что в ответе есть сообщение об ошибке
    assert "detail" in response.json()
