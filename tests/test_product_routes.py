def test_should_create_product(client):
    response = client.post(
        "/products",
        json={
            "url": "https://example.com/produto-teste",
            "name": "Produto Teste",
            "target_price": 100,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["url"] == "https://example.com/produto-teste"
    assert data["name"] == "Produto Teste"
    assert data["target_price"] == 100
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data


def test_should_list_products(client):
    client.post(
        "/products",
        json={
            "url": "https://example.com/produto-listagem",
            "name": "Produto Listagem",
            "target_price": 150,
        },
    )

    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Produto Listagem"
    assert data[0]["target_price"] == 150


def test_should_get_product_by_id(client):
    create_response = client.post(
        "/products",
        json={
            "url": "https://example.com/produto-busca",
            "name": "Produto Busca",
            "target_price": 200,
        },
    )

    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Produto Busca"
    assert data["target_price"] == 200


def test_should_return_404_when_product_does_not_exist(client):
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Produto não encontrado.",
    }


def test_should_update_product(client):
    create_response = client.post(
        "/products",
        json={
            "url": "https://example.com/produto-atualizar",
            "name": "Produto Antigo",
            "target_price": 100,
        },
    )

    product_id = create_response.json()["id"]

    response = client.patch(
        f"/products/{product_id}",
        json={
            "name": "Produto Atualizado",
            "target_price": 80,
            "is_active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Produto Atualizado"
    assert data["target_price"] == 80
    assert data["is_active"] is False


def test_should_delete_product(client):
    create_response = client.post(
        "/products",
        json={
            "url": "https://example.com/produto-remover",
            "name": "Produto Remover",
            "target_price": 300,
        },
    )

    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/products/{product_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 404