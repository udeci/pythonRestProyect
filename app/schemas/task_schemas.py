"""DTOs del módulo de tareas en background (ejemplo de threading)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    seconds: float = Field(2.0, ge=0, le=30, description="Duración simulada de la tarea")
    fail: bool = Field(False, description="Forzar que la tarea termine en error")


class TaskCreatedResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[int] = None
