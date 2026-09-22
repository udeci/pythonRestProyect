"""Lógica de negocio de usuarios: registro, autenticación y emisión de JWT."""

from __future__ import annotations

import sqlite3
from typing import NamedTuple

from app.repositories import user_repository
from app.schemas.user_schemas import LoginResponse, TokenResponse, UserRegister
from app.security.jwt_handler import create_access_token
from app.security.password_hasher import hash_password, verify_password

ALLOWED_ROLES = {"user", "admin"}


class UsernameAlreadyExistsError(Exception):
    """El username ya está registrado (violación de constraint UNIQUE)."""


class InvalidCredentialsError(Exception):
    """El usuario no existe o la contraseña no coincide."""


class AuthenticatedUser(NamedTuple):
    user_id: int
    username: str
    role: str


def register_user(payload: UserRegister) -> str:
    """Registra un usuario nuevo y devuelve el rol efectivo asignado."""
    role = payload.role if payload.role in ALLOWED_ROLES else "user"
    password_hash = hash_password(payload.password)

    try:
        user_repository.create(payload.username, password_hash, role)
    except sqlite3.IntegrityError as exc:
        raise UsernameAlreadyExistsError(payload.username) from exc

    return role


def authenticate(username: str, password: str) -> AuthenticatedUser:
    """Valida credenciales y devuelve los datos del usuario autenticado."""
    row = user_repository.find_by_username(username)
    if row is None or not verify_password(password, row["password_hash"]):
        raise InvalidCredentialsError(username)

    return AuthenticatedUser(user_id=row["id"], username=row["username"], role=row["role"])


def login(username: str, password: str) -> LoginResponse:
    """Autentica y arma la respuesta de login (incluye el JWT)."""
    user = authenticate(username, password)
    token = create_access_token(subject=user.username, role=user.role)

    return LoginResponse(
        message="Login exitoso",
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        token=token,
    )


def issue_token(username: str, password: str) -> TokenResponse:
    """Autentica y devuelve un token en formato OAuth2 (para Swagger)."""
    user = authenticate(username, password)
    token = create_access_token(subject=user.username, role=user.role)
    return TokenResponse(access_token=token, role=user.role)
