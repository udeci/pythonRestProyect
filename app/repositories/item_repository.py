"""Repositorio de items: única capa que conoce SQL para la tabla `items`."""

from __future__ import annotations

import sqlite3
from typing import List, Optional

from app.db.database import db_session


def find_all() -> List[sqlite3.Row]:
    with db_session() as conn:
        return conn.execute("SELECT * FROM items ORDER BY id").fetchall()


def find_by_id(item_id: int) -> Optional[sqlite3.Row]:
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()


def create(name: str, description: Optional[str], price: float, owner: str) -> int:
    with db_session() as conn:
        cursor = conn.execute(
            "INSERT INTO items (name, description, price, owner) VALUES (?, ?, ?, ?)",
            (name, description, price, owner),
        )
        return cursor.lastrowid


def update(item_id: int, name: str, description: Optional[str], price: float) -> None:
    with db_session() as conn:
        conn.execute(
            "UPDATE items SET name = ?, description = ?, price = ? WHERE id = ?",
            (name, description, price, item_id),
        )


def delete(item_id: int) -> None:
    with db_session() as conn:
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
