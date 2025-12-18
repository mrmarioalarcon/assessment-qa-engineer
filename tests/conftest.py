import pytest
from fastapi.testclient import TestClient
from app.main import app, fake_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def reset_db():
    fake_db["products"] = {}
    fake_db["product_counter"] = 0
    yield
    fake_db["products"] = {}
    fake_db["product_counter"] = 0


@pytest.fixture
def admin_token(client):
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]


@pytest.fixture
def user_token(client):
    response = client.post("/auth/login", json={
        "username": "user",
        "password": "user123"
    })
    return response.json()["access_token"]
