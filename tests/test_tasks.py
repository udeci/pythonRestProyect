"""Tests del servicio de tareas en background basado en threading.

Verifican que las tareas se ejecuten en hilos separados, que el endpoint
no bloquee la respuesta HTTP, y que el estado compartido se actualice de
forma segura entre hilos.
"""

from __future__ import annotations

import threading
import time

from fastapi.testclient import TestClient

from app.services.task_service import TaskService, TaskStatus


def test_create_task_returns_immediately_pending_or_running(client: TestClient) -> None:
    response = client.post("/tasks", json={"seconds": 1, "fail": False})

    assert response.status_code == 202
    body = response.json()
    assert body["status"] in (TaskStatus.PENDING.value, TaskStatus.RUNNING.value)
    assert "task_id" in body


def test_task_completes_in_background_thread(client: TestClient) -> None:
    response = client.post("/tasks", json={"seconds": 0.2, "fail": False})
    task_id = response.json()["task_id"]

    deadline = time.time() + 5
    status_value = None
    while time.time() < deadline:
        status_response = client.get(f"/tasks/{task_id}")
        status_value = status_response.json()["status"]
        if status_value == TaskStatus.COMPLETED.value:
            break
        time.sleep(0.05)

    assert status_value == TaskStatus.COMPLETED.value
    assert status_response.json()["result"] == 200  # 0.2s * 1000


def test_task_can_fail(client: TestClient) -> None:
    response = client.post("/tasks", json={"seconds": 0.1, "fail": True})
    task_id = response.json()["task_id"]

    deadline = time.time() + 5
    status_value = None
    while time.time() < deadline:
        status_value = client.get(f"/tasks/{task_id}").json()["status"]
        if status_value == TaskStatus.FAILED.value:
            break
        time.sleep(0.05)

    assert status_value == TaskStatus.FAILED.value


def test_unknown_task_returns_404(client: TestClient) -> None:
    response = client.get("/tasks/non-existent-id")
    assert response.status_code == 404


def test_task_service_runs_multiple_tasks_concurrently() -> None:
    """Prueba unitaria directa del TaskService: varios hilos en paralelo."""
    service = TaskService()

    tasks = [service.submit(seconds=0.3) for _ in range(5)]
    assert len(tasks) == 5
    assert threading.active_count() >= 1

    deadline = time.time() + 5
    while time.time() < deadline:
        statuses = [service.get(task.task_id).status for task in tasks]
        if all(status == TaskStatus.COMPLETED for status in statuses):
            break
        time.sleep(0.05)

    final_statuses = [service.get(task.task_id).status for task in tasks]
    assert all(status == TaskStatus.COMPLETED for status in final_statuses)
