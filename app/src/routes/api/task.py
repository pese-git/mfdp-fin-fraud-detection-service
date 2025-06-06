from fastapi import APIRouter, Body, Depends
from sqlmodel import Session
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.task import Task
import src.services.crud.task as TaskService
from typing import Any, List, cast
from src.services.logging.logging import get_logger

task_router = APIRouter(tags=["Tasks"])


logger = get_logger(logger_name='task_router')


@task_router.get("/", response_model=List[Task])
async def retrieve_all_tasks(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> List[Task]:
    logger.info(f"Пользователь {user.get('email', '[Unknown user]')} запрашивает все задачи")
    try:
        tasks = cast(List[Task], TaskService.get_all_tasks(session=session))
        logger.info(f"Получено задач: {len(tasks)}")
        return tasks
    except Exception as e:
        logger.error(f"Ошибка при получении всех задач: {e}", exc_info=True)
        raise


@task_router.get("/{id}", response_model=Task)
async def retrieve_task(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Task:
    logger.info(f"Пользователь {user.get('email', '[Unknown user]')} запрашивает задачу id={id}")
    task = TaskService.get_task_by_id(id, session=session)
    if not task:
        logger.warning(f"Задача id={id} не найдена")
    else:
        logger.debug(f"Задача id={id} получена: {task}")
    return task


@task_router.post("/new")
async def create_task(
    body: Task = Body(...),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Task:
    logger.info(f"Пользователь {user.get('email', '[Unknown user]')} создает задачу: {body}")
    try:
        new_task = TaskService.create_task(body, session=session)
        logger.info(f"Задача создана с id={new_task.id}")
        return new_task
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}", exc_info=True)
        raise


@task_router.delete("/{id}")
async def delete_task(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Task:
    logger.info(f"Пользователь {user.get('email', '[Unknown user]')} удаляет задачу id={id}")
    try:
        task = TaskService.delete_task_by_id(id, session=session)
        logger.info(f"Задача id={id} удалена")
        return task
    except Exception as e:
        logger.error(f"Ошибка при удалении задачи id={id}: {e}", exc_info=True)
        raise


@task_router.delete("/")
async def delete_tasks(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> dict[str, Any]:
    logger.info(f"Пользователь {user.get('email', '[Unknown user]')} удаляет все задачи")
    try:
        TaskService.delete_all_tasks(session=session)
        logger.info("Все задачи удалены")
        return {"message": "Задачи удалены успешно"}
    except Exception as e:
        logger.error(f"Ошибка при удалении всех задач: {e}", exc_info=True)
        raise