"""Dependencias de seguridad de FastAPI.

Equivalen al `SecurityFilterChain` + anotaciones `@PreAuthorize` de Spring
Security: interceptan cada request, extraen y validan el JWT del header
`Authorization: Bearer <token>`, resuelven el usuario autenticado
(`get_current_user`) y exponen una fábrica de dependencias para exigir
roles concretos (`require_role`), equivalente a
`@PreAuthorize("hasRole('ADMIN')")`.
"""

from __future__ import annotations

from typing import Callable, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.security.jwt_handler import decode_access_token

# Declara el esquema de seguridad "Bearer JWT" que Swagger UI renderiza
# como el botón "Authorize" (candado) en /docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


class CurrentUser(BaseModel):
    username: str
    role: str


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """Resuelve el usuario autenticado a partir del JWT de la petición."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    return CurrentUser(username=username, role=role)


def require_role(*allowed_roles: str) -> Callable[..., CurrentUser]:
    """Fábrica de dependencias para autorizar por rol (RBAC).

    Uso: `Depends(require_role("admin"))`, equivalente a
    `@PreAuthorize("hasRole('ADMIN')")` en Spring Security.
    """

    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para esta operación",
            )
        return current_user

    return role_checker
