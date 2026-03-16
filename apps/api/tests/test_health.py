from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_service_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "research-method-platform-api"
    assert payload["status"] == "ready"


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

