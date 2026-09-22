"""Emisión y verificación de tokens JWT (equivalente a `JwtTokenProvider`)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from app.core.config import settings


def create_access_token(
    subject: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Genera un JWT firmado con el usuario (`sub`) y su rol (`role`)."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    payload: Dict[str, Any] = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodifica y valida un JWT. Lanza `jwt.PyJWTError` si es inválido."""
    return jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
