import pytest

from app.demo import seed_demo_data
from app.models.price_history import PriceHistory
from app.models.product import Product


def test_demo_should_expose_sample_data_and_read_only_header(demo_client):
    response = demo_client.get("/products")

    assert response.status_code == 200
    assert response.headers["X-Demo-Mode"] == "read-only"
    assert [product["name"] for product in response.json()] == [
        "A Light in the Attic",
        "Tipping the Velvet",
    ]

    history_response = demo_client.get("/products/1/history")
    alert_response = demo_client.get("/products/1/alert")

    assert history_response.status_code == 200
    assert len(history_response.json()) == 3
    assert alert_response.status_code == 200
    assert alert_response.json()["alert_triggered"] is True


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "post",
            "/products",
            {
                "url": "https://books.toscrape.com/produto-demo",
                "name": "Produto Demo",
                "target_price": 100,
            },
        ),
        ("patch", "/products/1", {"target_price": 25}),
        ("delete", "/products/1", None),
        ("post", "/products/1/scrape", None),
    ],
)
def test_demo_should_block_every_mutating_route(demo_client, method, path, payload):
    response = demo_client.request(method, path, json=payload)

    assert response.status_code == 403
    assert response.headers["X-Demo-Mode"] == "read-only"
    assert "somente leitura" in response.json()["detail"]


def test_demo_seed_should_be_idempotent(db_session):
    seed_demo_data(db_session)
    seed_demo_data(db_session)

    assert db_session.query(Product).count() == 2
    assert db_session.query(PriceHistory).count() == 5


def test_demo_system_routes_should_describe_read_only_mode(demo_client):
    root_response = demo_client.get("/")
    health_response = demo_client.get("/health")

    assert root_response.json()["demo_mode"] == "read-only"
    assert health_response.json() == {
        "status": "ok",
        "demo_mode": "read-only",
    }
