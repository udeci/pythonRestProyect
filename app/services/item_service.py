"""Lógica de negocio del CRUD de ejemplo `items`.

Aplica las reglas de autorización a nivel de dominio (dueño vs. admin) y
delega el acceso a datos en `item_repository`.
"""

from __future__ import annotations

import sqlite3
from typing import List, Optional

from app.repositories import item_repository
from app.schemas.item_schemas import ItemCreate, ItemPatch, ItemResponse, ItemUpdate
from app.security.dependencies import CurrentUser


class ItemNotFoundError(Exception):
    """No existe un item con el id solicitado."""


class ForbiddenItemAccessError(Exception):
    """El usuario no es dueño del item ni tiene rol admin."""


def _row_to_response(row: sqlite3.Row) -> ItemResponse:
    return ItemResponse(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        price=row["price"],
        owner=row["owner"],
    )


def _get_row_or_raise(item_id: int) -> sqlite3.Row:
    row = item_repository.find_by_id(item_id)
    if row is None:
        raise ItemNotFoundError(item_id)
    return row


def _ensure_owner_or_admin(row: sqlite3.Row, current_user: CurrentUser) -> None:
    if current_user.role != "admin" and row["owner"] != current_user.username:
        raise ForbiddenItemAccessError(row["id"])


def list_items() -> List[ItemResponse]:
    return [_row_to_response(row) for row in item_repository.find_all()]


def get_item(item_id: int) -> ItemResponse:
    row = _get_row_or_raise(item_id)
    return _row_to_response(row)


def create_item(payload: ItemCreate, current_user: CurrentUser) -> ItemResponse:
    item_id = item_repository.create(
        payload.name, payload.description, payload.price, current_user.username
    )
    return ItemResponse(
        id=item_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        owner=current_user.username,
    )


def replace_item(item_id: int, payload: ItemUpdate, current_user: CurrentUser) -> ItemResponse:
    """Reemplaza el item completo (semántica PUT: idempotente y total)."""
    row = _get_row_or_raise(item_id)
    _ensure_owner_or_admin(row, current_user)

    item_repository.update(item_id, payload.name, payload.description, payload.price)

    return ItemResponse(
        id=item_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        owner=row["owner"],
    )


def patch_item(item_id: int, payload: ItemPatch, current_user: CurrentUser) -> ItemResponse:
    """Actualiza parcialmente el item (semántica PATCH: solo campos enviados)."""
    row = _get_row_or_raise(item_id)
    _ensure_owner_or_admin(row, current_user)

    updates = payload.dict(exclude_unset=True)
    new_name = updates.get("name", row["name"])
    new_description = updates.get("description", row["description"])
    new_price = updates.get("price", row["price"])

    item_repository.update(item_id, new_name, new_description, new_price)

    return ItemResponse(
        id=item_id,
        name=new_name,
        description=new_description,
        price=new_price,
        owner=row["owner"],
    )


def delete_item(item_id: int) -> None:
    """Elimina el item. La autorización (rol admin) se valida en el controller."""
    _get_row_or_raise(item_id)
    item_repository.delete(item_id)
