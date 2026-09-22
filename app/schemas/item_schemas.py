"""DTOs del CRUD de ejemplo `items` (GET/POST/PUT/PATCH/DELETE)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, json_schema_extra={"example": "Teclado mecánico"})
    description: Optional[str] = Field(
        None, json_schema_extra={"example": "Switches azules, retroiluminado"}
    )
    price: float = Field(..., gt=0, json_schema_extra={"example": 59.99})


class ItemUpdate(BaseModel):
    """Payload para PUT: reemplaza el recurso completo (todos los campos)."""

    name: str = Field(..., min_length=1, json_schema_extra={"example": "Teclado mecánico RGB"})
    description: Optional[str] = Field(
        None, json_schema_extra={"example": "Switches rojos, RGB"}
    )
    price: float = Field(..., gt=0, json_schema_extra={"example": 69.99})


class ItemPatch(BaseModel):
    """Payload para PATCH: todos los campos son opcionales (actualización parcial)."""

    name: Optional[str] = Field(
        None, min_length=1, json_schema_extra={"example": "Teclado mecánico (oferta)"}
    )
    description: Optional[str] = Field(
        None, json_schema_extra={"example": "Nueva descripción"}
    )
    price: Optional[float] = Field(None, gt=0, json_schema_extra={"example": 49.99})


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    owner: str
