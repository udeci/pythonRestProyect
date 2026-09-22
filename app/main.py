"""Punto de creación de la aplicación FastAPI (application factory)."""

from __future__ import annotations

from typing import Dict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.controllers import item_controller, task_controller, user_controller
from app.core.config import settings
from app.db.database import init_db

tags_metadata = [
    {"name": "users", "description": "Registro, login y emisión de tokens JWT."},
    {
        "name": "tasks",
        "description": "Tareas en background ejecutadas con `threading` "
        "(ejemplo de concurrencia).",
    },
    {
        "name": "items",
        "description": "CRUD de ejemplo: GET, POST, PUT, PATCH y DELETE, "
        "con autorización basada en roles (RBAC).",
    },
    {"name": "health", "description": "Chequeo de salud del servicio."},
]


def create_app() -> FastAPI:
    """Application factory: crea e inicializa la app FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Servicio REST de ejemplo con FastAPI, organizado en capas "
            "controller/service/repository. Incluye documentación Swagger "
            "(OpenAPI) automática, autenticación JWT con roles (estilo "
            "Spring Security) y un módulo de tareas en background usando "
            "threading."
        ),
        version=settings.app_version,
        openapi_tags=tags_metadata,
    )

    init_db()

    app.include_router(user_controller.router)
    app.include_router(task_controller.router)
    app.include_router(item_controller.router)

    @app.get("/health", tags=["health"], summary="Chequeo de salud")
    def health_check() -> Dict[str, str]:
        return {"status": "ok"}

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=tags_metadata,
        )
        # Declara el esquema de seguridad Bearer JWT para que Swagger UI
        # muestre el botón "Authorize" (candado) en /docs.
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/token",
                        "scopes": {},
                    }
                },
            }
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]

    return app


app = create_app()
