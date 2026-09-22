"""Controller de usuarios: registro, login y emisión de token OAuth2."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user_schemas import (
    LoginResponse,
    MessageResponse,
    TokenResponse,
    UserCredentials,
    UserRegister,
)
from app.services import user_service

router = APIRouter(tags=["users"])


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description=(
        "Crea un usuario con contraseña hasheada (bcrypt) y un rol "
        "(`user` o `admin`) que luego se usa para autorización (RBAC) "
        "sobre el CRUD de items."
    ),
)
def register(payload: UserRegister) -> MessageResponse:
    try:
        role = user_service.register_user(payload)
    except user_service.UsernameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya existe",
        ) from exc

    return MessageResponse(
        message=f"Usuario '{payload.username}' registrado con rol '{role}'"
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login (devuelve un JWT real)",
    description=(
        "Valida las credenciales y devuelve un JWT firmado que debe "
        "enviarse en las siguientes peticiones como "
        "`Authorization: Bearer <token>`."
    ),
)
def login(credentials: UserCredentials) -> LoginResponse:
    try:
        return user_service.login(credentials.username, credentials.password)
    except user_service.InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos",
        ) from exc


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obtener token (flujo OAuth2 estándar, usado por el botón Authorize de Swagger)",
    description=(
        "Endpoint compatible con `OAuth2PasswordRequestForm` (form-data "
        "`username`/`password`). Es el que consume el botón *Authorize* "
        "de Swagger UI en `/docs` para autenticarte y probar los demás "
        "endpoints protegidos sin copiar el token manualmente."
    ),
)
def issue_token(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    try:
        return user_service.issue_token(form_data.username, form_data.password)
    except user_service.InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos",
        ) from exc
