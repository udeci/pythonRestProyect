"""Configuración centralizada de la aplicación (equivalente a application.yml)."""

from __future__ import annotations

import os


class Settings:
    app_name: str = "pythonRestProyect API"
    app_version: str = "1.0.0"

    database_path: str = os.environ.get("USERS_DB_PATH", "users.db")

    # En producción, `jwt_secret_key` debe provenir de una variable de
    # entorno / secret manager, nunca hardcodeada en el repositorio.
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY", "insecure-dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.environ.get("JWT_EXPIRE_MINUTES", "30"))


settings = Settings()
