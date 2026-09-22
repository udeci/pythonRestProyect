"""Controller del CRUD de ejemplo `items`: GET, POST, PUT, PATCH y DELETE.

Reglas de autorización (RBAC):
- GET (listar / detalle): público, no requiere token.
- POST (crear): requiere estar autenticado (cualquier rol).
- PUT (reemplazo completo) y PATCH (actualización parcial): requieren ser
  el dueño del item o tener rol `admin`.
- DELETE: requiere rol `admin` (equivalente a `@PreAuthorize("hasRole('ADMIN')")`).
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.item_schemas import ItemCreate, ItemPatch, ItemResponse, ItemUpdate
from app.security.dependencies import CurrentUser, get_current_user, require_role
from app.services import item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "",
    response_model=List[ItemResponse],
    summary="Listar items",
    description="Devuelve todos los items existentes. No requiere autenticación.",
)
def list_items() -> List[ItemResponse]:
    return item_service.list_items()


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Obtener un item por id",
    description="Devuelve el detalle de un item específico. No requiere autenticación.",
)
def get_item(item_id: int) -> ItemResponse:
    try:
        return item_service.get_item(item_id)
    except item_service.ItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} no encontrado",
        ) from exc


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un item",
    description=(
        "Crea un item nuevo asociado al usuario autenticado (`owner`). "
        "Requiere un JWT válido en `Authorization: Bearer <token>`."
    ),
)
def create_item(
    payload: ItemCreate,
    current_user: CurrentUser = Depends(get_current_user),
) -> ItemResponse:
    return item_service.create_item(payload, current_user)


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Reemplazar un item por completo",
    description=(
        "Reemplaza TODOS los campos del item (semántica idempotente de "
        "PUT). Si se omite un campo, la request es rechazada con 422 "
        "porque el esquema `ItemUpdate` los exige todos. Requiere ser el "
        "dueño del item o tener rol `admin`."
    ),
)
def replace_item(
    item_id: int,
    payload: ItemUpdate,
    current_user: CurrentUser = Depends(get_current_user),
) -> ItemResponse:
    try:
        return item_service.replace_item(item_id, payload, current_user)
    except item_service.ItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} no encontrado",
        ) from exc
    except item_service.ForbiddenItemAccessError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el dueño del item o un admin puede modificarlo",
        ) from exc


@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Actualizar parcialmente un item",
    description=(
        "Actualiza solo los campos enviados en el body (los demás quedan "
        "intactos), a diferencia de PUT que exige el recurso completo. "
        "Requiere ser el dueño del item o tener rol `admin`."
    ),
)
def patch_item(
    item_id: int,
    payload: ItemPatch,
    current_user: CurrentUser = Depends(get_current_user),
) -> ItemResponse:
    try:
        return item_service.patch_item(item_id, payload, current_user)
    except item_service.ItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} no encontrado",
        ) from exc
    except item_service.ForbiddenItemAccessError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el dueño del item o un admin puede modificarlo",
        ) from exc


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un item (solo admin)",
    description=(
        "Elimina un item de forma permanente. Requiere rol `admin`, "
        "equivalente a `@PreAuthorize(\"hasRole('ADMIN')\")` en Spring Security."
    ),
)
def delete_item(
    item_id: int,
    _current_user: CurrentUser = Depends(require_role("admin")),
) -> None:
    try:
        item_service.delete_item(item_id)
    except item_service.ItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} no encontrado",
        ) from exc
