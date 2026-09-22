"""Capa de seguridad de la aplicación (autenticación + autorización).

Cumple el mismo rol que Spring Security en un proyecto Java:
- `jwt_handler.py`   -> emisión/validación de tokens (JwtTokenProvider)
- `password_hasher.py` -> hashing de contraseñas (PasswordEncoder)
- `dependencies.py`  -> filtro de autenticación + chequeo de roles
                        (SecurityFilterChain + @PreAuthorize)
"""
