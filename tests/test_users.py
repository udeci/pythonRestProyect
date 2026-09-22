"""Tests de registro, login y emisión de token (autenticación)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_new_user(client: TestClient) -> None:
    response = client.post(
        "/register",
        json={"username": "alice", "password": "s3cret"},
    )
    assert response.status_code == 201
    assert "user" in response.json()["message"]


def test_register_with_admin_role(client: TestClient) -> None:
    response = client.post(
        "/register",
        json={"username": "root", "password": "s3cret", "role": "admin"},
    )
    assert response.status_code == 201
    assert "admin" in response.json()["message"]


def test_register_duplicate_user_returns_conflict(client: TestClient) -> None:
    client.post("/register", json={"username": "bob", "password": "pass123"})
    response = client.post("/register", json={"username": "bob", "password": "otro"})

    assert response.status_code == 409
    assert response.json()["detail"] == "El nombre de usuario ya existe"


def test_login_with_valid_credentials_returns_jwt(client: TestClient) -> None:
    client.post("/register", json={"username": "carol", "password": "mypassword"})

    response = client.post(
        "/login",
        json={"username": "carol", "password": "mypassword"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "carol"
    assert body["role"] == "user"
    assert body["message"] == "Login exitoso"
    # El JWT tiene 3 segmentos separados por "." (header.payload.signature).
    assert body["token"].count(".") == 2


def test_login_with_invalid_password_returns_unauthorized(client: TestClient) -> None:
    client.post("/register", json={"username": "dave", "password": "correct"})

    response = client.post(
        "/login",
        json={"username": "dave", "password": "wrong"},
    )

    assert response.status_code == 401


def test_login_with_unknown_user_returns_unauthorized(client: TestClient) -> None:
    response = client.post(
        "/login",
        json={"username": "ghost", "password": "whatever"},
    )

    assert response.status_code == 401


def test_token_endpoint_supports_oauth2_form_flow(client: TestClient) -> None:
    """El endpoint /token es el que usa el botón Authorize de Swagger UI."""
    client.post("/register", json={"username": "erin", "password": "mypassword"})

    response = client.post(
        "/token",
        data={"username": "erin", "password": "mypassword"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "user"
    assert "access_token" in body
