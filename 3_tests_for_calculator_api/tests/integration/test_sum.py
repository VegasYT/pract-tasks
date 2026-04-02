import pytest
from fastapi.testclient import TestClient


# (a, b, ожидаемый результат)
@pytest.mark.parametrize("a, b, expected", [
    (3, 5, 8),
    (-3, -5, -8),
    (7, 0, 7),
    (0, -4, -4),
])
def test_sum(client: TestClient, a: float, b: float, expected: float) -> None:
    response = client.get("/v1/calc/sum", params={"a": a, "b": b})

    assert response.status_code == 200
    assert response.json() == {"result": expected}
