import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from src.models.task import Task
from src.services.crud.task import (
    get_all_tasks,
    get_task_by_id,
    create_task,
    delete_task_by_id,
    delete_all_tasks,
)

from common.test_router_common import session_fixture


def test_create_task(session: Session) -> None:
    new_task = Task(task_id="abc123", status="init", model_id=1)
    created_task = create_task(new_task, session)
    assert created_task is not None
    assert created_task.id is not None
    assert created_task.task_id == "abc123"


def test_get_all_tasks(session: Session) -> None:
    tasks = [
        Task(task_id="task1", status="done", model_id=1),
        Task(task_id="task2", status="pending", model_id=1),
    ]
    session.add_all(tasks)
    session.commit()

    retrieved_tasks = get_all_tasks(session)
    assert len(retrieved_tasks) == 2
    assert all(isinstance(t, Task) for t in retrieved_tasks)


def test_get_task_by_id(session: Session) -> None:
    task = Task(task_id="unique_task", status="active", model_id=1)
    session.add(task)
    session.commit()

    retrieved_task = get_task_by_id(task.id, session)
    assert retrieved_task is not None
    assert retrieved_task.id == task.id


def test_delete_task_by_id(session: Session) -> None:
    task = Task(task_id="delete_task", status="completed", model_id=1)
    session.add(task)
    session.commit()

    deleted_task = delete_task_by_id(task.id, session)
    assert deleted_task.id == task.id
    assert get_task_by_id(task.id, session) is None


def test_delete_all_tasks(session: Session) -> None:
    session.add_all(
        [
            Task(task_id="task1", status="pending", model_id=1),
            Task(task_id="task2", status="done", model_id=1),
        ]
    )
    session.commit()

    delete_all_tasks(session)
    assert len(get_all_tasks(session)) == 0
