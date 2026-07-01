from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_should_return_api_message():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "API de Monitoramento de Preços está funcionando!",
        "docs": "/docs",
    }


def test_health_check_should_return_ok_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }