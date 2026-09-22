"""Controller de tareas en background (ejemplo de concurrencia con threading)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.task_schemas import (
    TaskCreatedResponse,
    TaskCreateRequest,
    TaskStatusResponse,
)
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Lanzar una tarea en background",
    description=(
        "Lanza una tarea en un hilo (`threading.Thread`) nuevo y responde "
        "inmediatamente sin bloquear la petición HTTP."
    ),
)
def create_task(payload: TaskCreateRequest) -> TaskCreatedResponse:
    task = task_service.submit(seconds=payload.seconds, fail=payload.fail)
    return TaskCreatedResponse(task_id=task.task_id, status=task.status.value)


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    summary="Consultar el estado de una tarea",
    description="Consulta el estado actual de una tarea previamente lanzada.",
)
def get_task_status(task_id: str) -> TaskStatusResponse:
    task = task_service.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status.value,
        result=task.result,
    )
