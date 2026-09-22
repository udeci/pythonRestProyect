"""Hashing y verificación de contraseñas (equivalente a `PasswordEncoder`)."""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Genera el hash bcrypt de una contraseña en texto plano."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica que la contraseña en texto plano coincida con el hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
