from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data


def test_health_app_name():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["app"] == "SELL INTELIGÊNCIA"


def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
