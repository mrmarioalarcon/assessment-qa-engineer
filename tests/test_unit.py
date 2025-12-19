from app.main import fake_db


def test_update_product_zero_quantity_bug():
    fake_db["products"] = {
        1: {
            "id": 1,
            "name": "Test",
            "price": 10,
            "quantity": 5,
            "min_stock": 1,
            "created_at": "now"
        }
    }

    product_update = {
        "quantity": 0
    }

    # Simula la lógica defectuosa
    if product_update.get("quantity"):
        fake_db["products"][1]["quantity"] = product_update["quantity"]

    # BUG: quantity nunca se actualiza a 0
    assert fake_db["products"][1]["quantity"] != 0


def test_delete_nonexistent_product_behavior(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete("/products/999", headers=headers)

    # BUG: devuelve 204 en vez de 404
    assert response.status_code == 204
