import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session
from fastapi import status

from src.models.task import Task
from common.test_router_common import (
    client_fixture,
    session_fixture,
    secret_key_fixture,
    create_test_user_fixture,
    test_token_fixture,
    username_fixture,
    password_fixture,
    email_fixture,
)


def test_retrieve_all_tasks(client: TestClient, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/tasks/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task(client: TestClient, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}

    task_id = "{}".format(uuid.uuid4())
    new_task_data = {
        "task_id": task_id,
        "status": "init",
        "model_id": 0,
    }
    response = client.post("/api/tasks/new", json=new_task_data, headers=headers)

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["task_id"] == new_task_data["task_id"]
    assert response_data["status"] == new_task_data["status"]


def test_retrieve_task(client: TestClient, session: Session, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    task_id = "{}".format(uuid.uuid4())
    new_task = Task(task_id=task_id, status="init")
    session.add(new_task)
    session.commit()
    response = client.get(f"/api/tasks/{new_task.id}", headers=headers)
    assert response.status_code == 200
    task_data = response.json()
    assert task_data["task_id"] == new_task.task_id
    assert task_data["status"] == new_task.status


def test_delete_task(client: TestClient, session: Session, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    task_id = "{}".format(uuid.uuid4())
    new_task = Task(task_id=task_id, status="init")

    session.add(new_task)
    session.commit()

    response = client.delete(f"/api/tasks/{new_task.id}", headers=headers)

    assert response.status_code == 200
    assert session.get(Task, new_task.id) is None


def test_delete_all_tasks(
    client: TestClient, session: Session, test_token: str
) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    task_id_1 = "{}".format(uuid.uuid4())
    task_id_2 = "{}".format(uuid.uuid4())

    session.add(Task(task_id=task_id_1, status="init"))
    session.add(Task(task_id=task_id_2, status="init"))
    session.commit()

    response = client.delete("/api/tasks/", headers=headers)

    assert response.status_code == 200
    assert session.query(Task).count() == 0
