"""Servicio de tareas en background usando `threading`.

Este módulo es el ejemplo de concurrencia del proyecto: cada tarea se
ejecuta en su propio hilo (`threading.Thread`), mientras el estado
compartido (`_tasks`) se protege con un `threading.Lock` para evitar
condiciones de carrera entre el hilo de la tarea y el hilo que atiende
la petición HTTP de consulta de estado.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[int] = None
    error: Optional[str] = None


class TaskService:
    """Administra la ejecución concurrente de tareas de cómputo simuladas."""

    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()

    def submit(self, seconds: float = 2.0, fail: bool = False) -> Task:
        """Crea una tarea y la ejecuta en un hilo nuevo.

        Args:
            seconds: tiempo simulado de procesamiento.
            fail: si True, la tarea terminará en estado FAILED.
        """
        task_id = str(uuid.uuid4())
        task = Task(task_id=task_id, status=TaskStatus.PENDING)

        with self._lock:
            self._tasks[task_id] = task

        thread = threading.Thread(
            target=self._run_task,
            args=(task_id, seconds, fail),
            daemon=True,
        )
        thread.start()

        return task

    def _run_task(self, task_id: str, seconds: float, fail: bool) -> None:
        with self._lock:
            self._tasks[task_id].status = TaskStatus.RUNNING

        time.sleep(seconds)

        with self._lock:
            task = self._tasks[task_id]
            if fail:
                task.status = TaskStatus.FAILED
                task.error = "Simulated failure"
            else:
                task.status = TaskStatus.COMPLETED
                task.result = int(seconds * 1000)

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            # Devolvemos una copia para no exponer el objeto mutable compartido.
            return Task(
                task_id=task.task_id,
                status=task.status,
                result=task.result,
                error=task.error,
            )


# Instancia única compartida por toda la aplicación (patrón singleton simple).
task_service = TaskService()
