from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "Audio Emotion Client Demo",
        "version": "0.1.0",
        "environment": "development",
    }
