# pythonRestProyect

Servicio REST de ejemplo en **Python + FastAPI**, organizado en capas
`controller / service / repository` (como un proyecto Spring Boot), con:

- **Swagger/OpenAPI** automático (`/docs` y `/redoc`).
- **Seguridad tipo "Spring Security"**: JWT + roles (`user`/`admin`) con
  dependencias de FastAPI que actúan como filtro de autenticación y como
  `@PreAuthorize`.
- **Concurrencia con `threading`**: tareas en background ejecutadas en
  hilos independientes.
- **CRUD completo de ejemplo** (`items`) cubriendo los 5 verbos HTTP:
  `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.
- Suite de tests con `pytest` (27 tests).

---

## 1. Arquitectura del proyecto

```
app/
├── controllers/          # Capa HTTP (equivalente a @RestController)
│   ├── user_controller.py    # /register, /login, /token
│   ├── task_controller.py    # /tasks (ejemplo de threading)
│   └── item_controller.py    # /items (GET/POST/PUT/PATCH/DELETE)
├── services/              # Lógica de negocio (equivalente a @Service)
│   ├── user_service.py
│   ├── task_service.py        # TaskService: hilos + lock
│   └── item_service.py
├── repositories/           # Acceso a datos (equivalente a @Repository)
│   ├── user_repository.py
│   └── item_repository.py
├── schemas/                # DTOs Pydantic (request/response)
│   ├── user_schemas.py
│   ├── task_schemas.py
│   └── item_schemas.py
├── security/                # "Spring Security" del proyecto
│   ├── jwt_handler.py          # emitir/validar JWT
│   ├── password_hasher.py       # hash/verify con bcrypt
│   └── dependencies.py          # get_current_user, require_role (RBAC)
├── db/
│   └── database.py             # conexión SQLite thread-safe
├── core/
│   └── config.py               # configuración centralizada (settings)
└── main.py                     # application factory de FastAPI

tests/
├── conftest.py           # fixtures: client de pruebas + DB temporal
├── test_users.py          # registro / login / token
├── test_tasks.py           # ejemplo de threading
└── test_items.py           # GET/POST/PUT/PATCH/DELETE + RBAC

run.py                      # entrypoint (uvicorn)
requirements.txt / requirements-dev.txt
pyproject.toml               # configuración de pytest
```

Cada capa tiene una única responsabilidad, igual que en un proyecto
Java/Spring:

| Capa | Responsabilidad | Analogía Spring |
|---|---|---|
| `controllers/` | Recibe la request HTTP, valida el DTO de entrada, delega en el service y traduce las excepciones de dominio a códigos HTTP. | `@RestController` |
| `services/` | Contiene las reglas de negocio (por ejemplo, "solo el dueño o un admin puede editar un item"). No sabe nada de HTTP ni de SQL. | `@Service` |
| `repositories/` | Es la única capa que ejecuta SQL. No contiene lógica de negocio. | `@Repository` / Spring Data |
| `security/` | Autenticación (JWT) y autorización (roles). | Spring Security |

---

## 2. Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

## 3. Ejecutar el servidor

```bash
python run.py
```

La API queda disponible en `http://localhost:8000`.

---

## 4. Swagger / OpenAPI ("el Swagger en Python")

FastAPI genera automáticamente la documentación interactiva a partir del
código (tipos Pydantic + metadatos de cada endpoint):

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc** (documentación de solo lectura, más limpia): http://localhost:8000/redoc
- **Esquema OpenAPI en crudo (JSON)**: http://localhost:8000/openapi.json

### Qué hacer en `/docs`

1. Abrí `http://localhost:8000/docs`.
2. Vas a ver los endpoints agrupados por tags: `users`, `tasks`, `items`, `health`.
3. Para probar un endpoint protegido (por ejemplo `POST /items`):
   - Primero ejecutá `POST /register` y `POST /login` (o usá el botón
     **Authorize** 🔒 arriba a la derecha, que usa `POST /token`).
   - En el botón **Authorize**, ingresá el `username`/`password` de un
     usuario ya registrado. Swagger llama a `/token` y guarda el JWT
     automáticamente en todas las peticiones siguientes.
   - Ahora podés probar `POST /items`, `PUT /items/{id}`, etc. sin copiar
     el token manualmente.
4. Cada endpoint muestra su `summary`, `description`, el schema de
   entrada/salida y ejemplos (`example`) definidos en `app/schemas/`.

---

## 5. Seguridad (el "Spring Security" de este proyecto)

La carpeta `app/security/` reproduce el flujo típico de Spring Security,
adaptado a FastAPI:

| Archivo | Rol |
|---|---|
| `jwt_handler.py` | Emite y valida tokens JWT firmados (HS256). Equivale a `JwtTokenProvider`. |
| `password_hasher.py` | Hashea/verifica contraseñas con `bcrypt`. Equivale a `PasswordEncoder`. |
| `dependencies.py` | `get_current_user`: extrae y valida el JWT del header `Authorization: Bearer <token>` (equivale al filtro de autenticación / `SecurityFilterChain`). `require_role(*roles)`: fábrica de dependencias para exigir un rol concreto (equivale a `@PreAuthorize("hasRole('ADMIN')")`). |

### Flujo de autenticación

1. **Registro** — `POST /register` crea un usuario con contraseña
   hasheada y un rol (`user` por defecto, o `admin`).
2. **Login** — `POST /login` valida credenciales y devuelve un JWT
   (`token`) además de metadata del usuario.
3. **Uso del token** — en cada request protegido, se envía:
   ```
   Authorization: Bearer <token>
   ```
4. **Autorización por rol** — algunos endpoints exigen un rol concreto
   (ver tabla de `items` más abajo). Si el rol no alcanza, la API
   responde `403 Forbidden`.

### Endpoints de autenticación

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/register` | Crea un usuario. Body: `{"username", "password", "role"}` (`role` opcional, `user` por defecto). |
| POST | `/login` | Devuelve un JWT (`token`) + datos del usuario. Body: `{"username", "password"}`. |
| POST | `/token` | Igual que `/login`, pero en formato `form-data` (`OAuth2PasswordRequestForm`). Es el que usa el botón *Authorize* de Swagger. |

```bash
# Registrar un admin
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"secret123","role":"admin"}'

# Login -> obtener JWT
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"secret123"}'
# {"message":"Login exitoso","user_id":1,"username":"admin1","role":"admin","token":"eyJ..."}
```

---

## 6. Ejemplo de threading (tareas en background)

`app/services/task_service.py` lanza cada tarea en un `threading.Thread`
independiente, mientras un `threading.Lock` protege el diccionario de
estados compartido entre hilos.

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/tasks` | Lanza una tarea en un hilo nuevo. Responde de inmediato (no bloqueante) con `status: pending`. |
| GET | `/tasks/{task_id}` | Consulta el estado actual (`pending` → `running` → `completed`/`failed`). |

```bash
# Lanza una tarea que "tarda" 2 segundos en un hilo separado
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
  -d '{"seconds": 2, "fail": false}'
# {"task_id": "...", "status": "pending"}   <- responde al instante

# Consultar el estado más tarde
curl http://localhost:8000/tasks/<task_id>
# {"task_id": "...", "status": "completed", "result": 2000}
```

`tests/test_tasks.py` incluye una prueba (`test_task_service_runs_multiple_tasks_concurrently`)
que lanza 5 tareas y verifica que todas se completen de forma concurrente.

---

## 7. CRUD de ejemplo `items`: GET, POST, PUT, PATCH y DELETE

Este es el ejemplo "claro" de los 5 verbos HTTP, con reglas de
autorización distintas en cada uno para mostrar cómo se combinan con la
capa de seguridad:

| Método | Ruta | Auth requerida | Qué hace / cuándo usarlo |
|---|---|---|---|
| **GET** | `/items` | Ninguna (público) | Lista todos los items. Usalo para explorar el catálogo sin necesidad de login. |
| **GET** | `/items/{id}` | Ninguna (público) | Devuelve el detalle de un item puntual. `404` si no existe. |
| **POST** | `/items` | JWT válido (cualquier rol) | Crea un item nuevo asociado al usuario autenticado (`owner`). Usalo cuando necesitás **crear** un recurso nuevo. |
| **PUT** | `/items/{id}` | JWT + (dueño o admin) | **Reemplaza el recurso completo.** Todos los campos son obligatorios; si falta uno, la API responde `422`. Usalo cuando querés sobreescribir un item entero (semántica idempotente: llamarlo 2 veces con el mismo body da el mismo resultado). |
| **PATCH** | `/items/{id}` | JWT + (dueño o admin) | **Actualiza solo los campos enviados**; el resto queda igual. Usalo para cambios parciales (por ejemplo, actualizar solo el precio) sin tener que reenviar todo el objeto. |
| **DELETE** | `/items/{id}` | JWT + rol `admin` | Elimina el item de forma permanente. Requiere explícitamente el rol `admin` (equivalente a `@PreAuthorize("hasRole('ADMIN')")`), para mostrar autorización basada en roles (RBAC) además de "dueño del recurso". |

### Ejemplos con `curl`

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"secret123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# GET - listar (público, sin token)
curl http://localhost:8000/items

# POST - crear (requiere token)
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Teclado mecánico","description":"Switches azules","price":59.99}'
# {"id":1,"name":"Teclado mecánico", ... ,"owner":"admin1"}

# PUT - reemplazo completo (todos los campos son obligatorios)
curl -X PUT http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Teclado mecánico RGB","description":"Switches rojos","price":69.99}'

# PATCH - actualización parcial (solo el precio)
curl -X PATCH http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"price":49.99}'

# DELETE - requiere rol admin
curl -X DELETE http://localhost:8000/items/1 \
  -H "Authorization: Bearer $TOKEN"
# 204 No Content
```

---

## 8. Ejecutar los tests

```bash
source venv/bin/activate
pytest
```

La suite tiene **27 tests**:

- `tests/test_users.py`: registro, roles, login (JWT), `/token` (OAuth2), credenciales inválidas.
- `tests/test_tasks.py`: creación no bloqueante de tareas, transición de estados en hilos, 5 tareas corriendo en paralelo.
- `tests/test_items.py`: los 5 verbos HTTP, incluyendo casos de éxito y de autorización (401 sin token, 403 sin permisos, 404 recurso inexistente, 422 payload inválido en PUT).

---

## 9. Notas de seguridad para producción

- Cambiá `JWT_SECRET_KEY` por una clave fuerte (≥32 bytes) vía variable
  de entorno; el valor por defecto en `app/core/config.py` es solo para
  desarrollo.
- Ajustá `JWT_EXPIRE_MINUTES` según la política de expiración que necesites.
- Este ejemplo usa SQLite por simplicidad; en producción se recomienda
  una base de datos gestionada (PostgreSQL, MySQL, etc.).
