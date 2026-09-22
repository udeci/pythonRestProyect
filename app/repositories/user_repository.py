"""Repositorio de usuarios: única capa que conoce SQL para la tabla `users`.

Equivalente a un `UserRepository` de Spring Data: no contiene lógica de
negocio, solo operaciones CRUD contra la base de datos.
"""

from __future__ import annotations

import sqlite3
from typing import Optional

from app.db.database import db_session


def find_by_username(username: str) -> Optional[sqlite3.Row]:
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def create(username: str, password_hash: str, role: str) -> int:
    """Inserta un usuario nuevo y devuelve su id.

    Lanza `sqlite3.IntegrityError` si el username ya existe (constraint
    UNIQUE), que la capa de servicio se encarga de traducir a un error
    de dominio.
    """
    with db_session() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        return cursor.lastrowid
