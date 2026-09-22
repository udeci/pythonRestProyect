"""Paquete principal de la aplicación REST de ejemplo.

Arquitectura en capas (similar a un proyecto Spring Boot):
- controllers/  -> capa de presentación HTTP (equivalente a @RestController)
- services/     -> lógica de negocio (equivalente a @Service)
- repositories/ -> acceso a datos (equivalente a @Repository)
- schemas/      -> DTOs / modelos Pydantic de entrada y salida
- security/     -> autenticación y autorización (JWT, roles)
- db/           -> conexión a la base de datos
- core/         -> configuración transversal (settings)
"""
