"""DTOs de usuarios y autenticación."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=1, description="Nombre de usuario")
    password: str = Field(..., min_length=1, description="Contraseña en texto plano")
    role: str = Field(
        "user",
        description="Rol del usuario: 'user' o 'admin'. Determina qué "
        "operaciones puede realizar (ver RBAC en README).",
    )


class UserCredentials(BaseModel):
    username: str = Field(..., min_length=1, description="Nombre de usuario")
    password: str = Field(..., min_length=1, description="Contraseña en texto plano")


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class LoginResponse(BaseModel):
    message: str
    user_id: int
    username: str
    role: str
    token: str
