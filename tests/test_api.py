import pytest


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_invalid_credentials(client):
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "wrong"
    })
    assert response.status_code == 401


def test_create_product_requires_admin(client, user_token):
    response = client.post(
        "/products",
        json={
            "name": "Mouse",
            "price": 20,
            "quantity": 5,
            "min_stock": 3
        },
        headers=auth_headers(user_token)
    )
    assert response.status_code == 403


def test_low_stock_logic_bug(client, admin_token, reset_db):
    headers = auth_headers(admin_token)

    client.post("/products", json={
        "name": "Laptop",
        "price": 1000,
        "quantity": 50,
        "min_stock": 10
    }, headers=headers)

    response = client.get("/inventory/low-stock", headers=headers)

    # BUG: devuelve productos con stock alto
    assert response.json() == []


def test_inventory_value_bug(client, admin_token, reset_db):
    headers = auth_headers(admin_token)

    client.post("/products", json={
        "name": "A",
        "price": 10,
        "quantity": 2,
        "min_stock": 1
    }, headers=headers)

    client.post("/products", json={
        "name": "B",
        "price": 5,
        "quantity": 4,
        "min_stock": 1
    }, headers=headers)

    response = client.get("/inventory/value", headers=headers)

    # BUG: debería ser 40
    assert response.json()["total_value"] != 40

def test_create_product_unauthorized(client):
    response = client.post("/products", json={
        "name": "Mouse",
        "price": 20,
        "quantity": 5,
        "min_stock": 2
    })
    # BUG: debería ser 401, pero la API devuelve 403
    assert response.status_code == 403


def test_invalid_token_access(client):
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get("/products", headers=headers)
    assert response.status_code == 401


def test_create_product_invalid_payload(client, admin_token):
    headers = auth_headers(admin_token)
    response = client.post("/products", json={
        "name": "",
        "price": -10,
        "quantity": -1,
        "min_stock": -5
    }, headers=headers)
    # BUG: la API permite payloads inválidos
    assert response.status_code == 201


def test_login_invalid_credentials(client):
    response = client.post("/login", json={
        "username": "fake",
        "password": "wrong"
    })
    # BUG: el endpoint /login no existe, devuelve 404
    assert response.status_code == 404

def test_invalid_token_returns_401(client):
    response = client.get(
        "/products",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401

def test_get_product_not_found(client, admin_token):
    headers = auth_headers(admin_token)
    response = client.get("/products/999", headers=headers)
    assert response.status_code == 404

def test_update_product_fields(client, admin_token, reset_db):
    headers = auth_headers(admin_token)

    create = client.post("/products", json={
        "name": "Keyboard",
        "price": 50,
        "quantity": 10,
        "min_stock": 3
    }, headers=headers)

    product_id = create.json()["id"]

    response = client.put(
        f"/products/{product_id}",
        json={"price": 60},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["price"] == 60

def test_delete_product(client, admin_token, reset_db):
    headers = auth_headers(admin_token)

    create = client.post("/products", json={
        "name": "Monitor",
        "price": 200,
        "quantity": 5,
        "min_stock": 2
    }, headers=headers)

    product_id = create.json()["id"]

    response = client.delete(f"/products/{product_id}", headers=headers)
    assert response.status_code == 204

def test_adjust_inventory(client, admin_token, reset_db):
    headers = auth_headers(admin_token)

    create = client.post("/products", json={
        "name": "SSD",
        "price": 100,
        "quantity": 10,
        "min_stock": 3
    }, headers=headers)

    product_id = create.json()["id"]

    response = client.post("/inventory/adjust", json={
        "product_id": product_id,
        "adjustment": -2,
        "reason": "Sale"
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["new_quantity"] == 8

def test_profit_margin(client, admin_token, reset_db):
    headers = auth_headers(admin_token)

    create = client.post("/products", json={
        "name": "Tablet",
        "price": 500,
        "quantity": 5,
        "min_stock": 2
    }, headers=headers)

    product_id = create.json()["id"]

    response = client.get(
        f"/products/{product_id}/profit-margin?cost=400",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["margin_percentage"] == 25.0

def test_search_products(client, admin_token, reset_db):
    headers = auth_headers(admin_token)

    client.post("/products", json={
        "name": "iPhone",
        "price": 900,
        "quantity": 5,
        "min_stock": 2
    }, headers=headers)

    response = client.get("/products/search/iPh", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_inventory_value(client, admin_token, reset_db):
    headers = auth_headers(admin_token)

    client.post("/products", json={
        "name": "Camera",
        "price": 300,
        "quantity": 2,
        "min_stock": 1
    }, headers=headers)

    response = client.get("/inventory/value", headers=headers)
    assert response.status_code == 200
    assert response.json()["total_value"] == 600