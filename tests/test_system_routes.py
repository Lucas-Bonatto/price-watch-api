from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_should_return_landing_page():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Radar de Preços" in response.text
    assert "Explorar documentação" in response.text


def test_api_info_should_return_api_message():
    response = client.get("/api")

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
