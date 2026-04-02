import pytest
from fastapi.testclient import TestClient


# (a, b, ожидаемый результат)
@pytest.mark.parametrize("a, b, expected", [
    (3, 4, 12),
    (-3, -4, 12),
    (3, -4, -12),
    (99, 0, 0),
    (0, -7, 0),
    (7, 1, 7),
    (-5, 1, -5),
])
def test_multiply(client: TestClient, a: float, b: float, expected: float) -> None:
    response = client.get("/v1/calc/multiply", params={"a": a, "b": b})

    assert response.status_code == 200
    assert response.json() == {"result": expected}
