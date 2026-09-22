"""Tests del CRUD de ejemplo `items`: GET, POST, PUT, PATCH y DELETE.

Cubren tanto el comportamiento funcional de cada verbo como las reglas
de autorización (RBAC): público vs autenticado vs dueño/admin.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_headers, register_and_login


def _create_item(client: TestClient, token: str, name: str = "Teclado", price: float = 50.0) -> dict:
    response = client.post(
        "/items",
        json={"name": name, "description": "desc", "price": price},
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()


# --- GET ----------------------------------------------------------------


def test_list_items_is_public(client: TestClient) -> None:
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_get_item_by_id_is_public(client: TestClient) -> None:
    token = register_and_login(client, "owner1", "pass123")
    item = _create_item(client, token)

    response = client.get(f"/items/{item['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Teclado"


def test_get_unknown_item_returns_404(client: TestClient) -> None:
    response = client.get("/items/999")
    assert response.status_code == 404


# --- POST -----------------------------------------------------------------


def test_create_item_requires_authentication(client: TestClient) -> None:
    response = client.post("/items", json={"name": "Mouse", "price": 20.0})
    assert response.status_code == 401


def test_create_item_with_valid_token(client: TestClient) -> None:
    token = register_and_login(client, "owner2", "pass123")
    item = _create_item(client, token, name="Monitor", price=199.99)

    assert item["name"] == "Monitor"
    assert item["owner"] == "owner2"


# --- PUT (reemplazo completo) -----------------------------------------------


def test_put_replaces_item_when_owner(client: TestClient) -> None:
    token = register_and_login(client, "owner3", "pass123")
    item = _create_item(client, token)

    response = client.put(
        f"/items/{item['id']}",
        json={"name": "Teclado RGB", "description": "nuevo", "price": 80.0},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Teclado RGB"
    assert body["price"] == 80.0


def test_put_missing_field_returns_422(client: TestClient) -> None:
    """PUT exige el recurso completo: si falta un campo, es 422."""
    token = register_and_login(client, "owner4", "pass123")
    item = _create_item(client, token)

    response = client.put(
        f"/items/{item['id']}",
        json={"name": "Solo nombre"},  # falta 'price'
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_put_forbidden_for_non_owner_non_admin(client: TestClient) -> None:
    owner_token = register_and_login(client, "owner5", "pass123")
    item = _create_item(client, owner_token)

    other_token = register_and_login(client, "intruder", "pass123")
    response = client.put(
        f"/items/{item['id']}",
        json={"name": "Hackeado", "price": 1.0},
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403


def test_put_allowed_for_admin_even_if_not_owner(client: TestClient) -> None:
    owner_token = register_and_login(client, "owner6", "pass123")
    item = _create_item(client, owner_token)

    admin_token = register_and_login(client, "admin1", "pass123", role="admin")
    response = client.put(
        f"/items/{item['id']}",
        json={"name": "Editado por admin", "price": 10.0},
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Editado por admin"


# --- PATCH (actualización parcial) ------------------------------------------


def test_patch_updates_only_sent_fields(client: TestClient) -> None:
    token = register_and_login(client, "owner7", "pass123")
    item = _create_item(client, token, name="Original", price=100.0)

    response = client.patch(
        f"/items/{item['id']}",
        json={"price": 150.0},  # solo actualizamos el precio
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Original"  # no cambió
    assert body["price"] == 150.0


def test_patch_forbidden_for_non_owner_non_admin(client: TestClient) -> None:
    owner_token = register_and_login(client, "owner8", "pass123")
    item = _create_item(client, owner_token)

    other_token = register_and_login(client, "intruder2", "pass123")
    response = client.patch(
        f"/items/{item['id']}",
        json={"price": 1.0},
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403


# --- DELETE (solo admin) -----------------------------------------------------


def test_delete_requires_admin_role(client: TestClient) -> None:
    token = register_and_login(client, "owner9", "pass123")
    item = _create_item(client, token)

    # El propio dueño, sin rol admin, no puede borrar.
    response = client.delete(f"/items/{item['id']}", headers=auth_headers(token))
    assert response.status_code == 403


def test_delete_succeeds_for_admin(client: TestClient) -> None:
    owner_token = register_and_login(client, "owner10", "pass123")
    item = _create_item(client, owner_token)

    admin_token = register_and_login(client, "admin2", "pass123", role="admin")
    response = client.delete(f"/items/{item['id']}", headers=auth_headers(admin_token))

    assert response.status_code == 204
    assert client.get(f"/items/{item['id']}").status_code == 404


def test_delete_requires_authentication(client: TestClient) -> None:
    token = register_and_login(client, "owner11", "pass123")
    item = _create_item(client, token)

    response = client.delete(f"/items/{item['id']}")
    assert response.status_code == 401
