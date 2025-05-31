from fastapi import APIRouter, Body, Depends
from sqlmodel import Session
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.task import Task
import src.services.crud.task as TaskService
from typing import Any, List, cast

task_router = APIRouter(tags=["Tasks"])


@task_router.get("/", response_model=List[Task])
async def retrieve_all_tasks(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> List[Task]:
    """
    Получить все задачи из базы данных.

    Этот эндпоинт извлекает все доступные задачи из базы данных,
    используя текущую сессию, предоставленную зависимостью get_session.

    Возвращает:
        List[Task]: Список всех объектов Task, извлеченных из базы данных.
    """
    return cast(List[Task], TaskService.get_all_tasks(session=session))


@task_router.get("/{id}", response_model=Task)
async def retrieve_task(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Task:
    """
    Получить одну задачу по её ID из базы данных.

    Этот эндпоинт извлекает конкретную задачу, идентифицированную предоставленным ID.
    Он использует текущую сессию, предоставленную зависимостью get_session.

    Аргументы:
        id (int): Уникальный идентификатор задачи для извлечения.
        session: Сессия базы данных, используемая для запросов задачи.

    Возвращает:
        Task: Объект Task, который соответствует предоставленному ID.
    """
    return TaskService.get_task_by_id(id, session=session)


@task_router.post("/new")
async def create_task(
    body: Task = Body(...),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Task:
    """
    Создать новую задачу в базе данных.

    Этот эндпоинт позволяет создать новую задачу, принимая объект Task
    из тела запроса. Он использует текущую сессию, предоставляемую
    зависимостью get_session, чтобы добавить задачу в базу данных.

    Аргументы:
        body (Task): Объект Task, содержащий детали задачи для создания.
        session: Сессия базы данных, используемая для добавления новой задачи.

    Возвращает:
        dict: Словарь, содержащий детали вновь созданной задачи.
    """
    new_task = TaskService.create_task(body, session=session)
    return new_task


@task_router.delete("/{id}")
async def delete_task(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Task:
    """
    Удалить задачу по её ID из базы данных.

    Этот эндпоинт позволяет удалить конкретную задачу, идентифицированную предоставленным ID.
    Он использует текущую сессию, предоставленную зависимостью get_session.

    Аргументы:
        id (int): Уникальный идентификатор задачи для удаления.
        session: Сессия базы данных, используемая для удаления задачи.

    Возвращает:
        dict: Словарь, указывающий на успешное удаление задачи.
    """
    return TaskService.delete_task_by_id(id, session=session)


@task_router.delete("/")
async def delete_tasks(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> dict[str, Any]:
    """
    Удалить все задачи из базы данных.

    Этот эндпоинт позволяет удалить все задачи, которые в настоящее время хранятся в базе данных.
    Он полагается на сессию, предоставленную зависимостью get_session, для выполнения операции удаления.

    Аргументы:
        session: Сессия базы данных, используемая для удаления всех задач.

    Возвращает:
        dict: Словарь с сообщением, указывающим на то, что все задачи успешно удалены.
    """
    TaskService.delete_all_tasks(session=session)
    return {"message": "Задачи удалены успешно"}
