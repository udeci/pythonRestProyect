"""Fixtures compartidos para los tests."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente de pruebas con una base de datos SQLite temporal y aislada."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["USERS_DB_PATH"] = db_path

    # Importamos después de fijar la variable de entorno para que
    # app.db.database use la ruta temporal.
    from app.db import database

    database.DATABASE_PATH = db_path

    from app.main import create_app

    app = create_app()

    with TestClient(app) as test_client:
        yield test_client

    os.close(db_fd)
    os.remove(db_path)


def register_and_login(client: TestClient, username: str, password: str, role: str = "user") -> str:
    """Helper: registra un usuario y devuelve su JWT (token de /login)."""
    client.post(
        "/register",
        json={"username": username, "password": password, "role": role},
    )
    response = client.post("/login", json={"username": username, "password": password})
    return response.json()["token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
