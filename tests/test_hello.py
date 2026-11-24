from fastapi.testclient import TestClient


def test_hello(client: TestClient) -> None:
    response = client.get("/api/v1/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
