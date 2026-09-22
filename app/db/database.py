"""Capa de conexión a la base de datos SQLite.

Provee un context manager thread-safe (protegido con `threading.Lock`)
para que tanto las peticiones HTTP como las tareas en background puedan
leer/escribir la base sin condiciones de carrera.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterator

from app.core.config import settings

# Se expone como variable de módulo (no solo vía `settings`) para que los
# tests puedan sobreescribirla fácilmente con una base de datos temporal.
DATABASE_PATH = settings.database_path

_db_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    """Crea una nueva conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    """Context manager que entrega una conexión y la cierra al finalizar."""
    with _db_lock:
        conn = get_connection()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def init_db() -> None:
    """Crea las tablas de usuarios e items si no existen."""
    with db_session() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                owner TEXT NOT NULL
            )
            """
        )
