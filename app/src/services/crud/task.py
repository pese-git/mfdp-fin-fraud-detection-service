from typing import List, Optional

from sqlmodel import Session
from src.models.task import Task
from src.services.logging.logging import get_logger

logger = get_logger(logger_name="TaskCRUD")


def get_all_tasks(session: Session) -> List[Task]:
    """
    Получить все задачи из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для выполнения запроса задач.

    Возвращает:
        Список объектов Task, представляющих все задачи в базе данных.
    """
    logger.info("Запрошен список всех задач")
    tasks = session.query(Task).all()
    logger.debug(f"Найдено {len(tasks)} задач")
    return tasks


def get_task_by_id(id: int, session: Session) -> Optional[Task]:
    """
    Получить задачу из базы данных по её ID.

    Аргументы:
        id: ID задачи, которую нужно получить.
        session: Сессия базы данных, используемая для выполнения запроса задачи.

    Возвращает:
        Объект Task, представляющий задачу с указанным ID,
        или None, если таких задач не найдено.
    """
    logger.info(f"Запрошена задача по id={id}")
    task = session.get(Task, id)
    if task:
        logger.debug(f"Задача с id={id} найдена")
        return task
    logger.warning(f"Задача с id={id} не найдена")
    return None


def create_task(new_task: Task, session: Session) -> Task | None:
    """
    Добавить новую задачу в базу данных и зафиксировать транзакцию.

    Аргументы:
        new_task: Объект Task, который будет добавлен в базу данных.
        session: Сессия базы данных, используемая для добавления задачи.

    Возвращает:
        None

    Эта функция добавляет предоставленный объект Task в сессию базы данных, фиксирует
    транзакцию для сохранения изменений и обновляет объект Task для отражения обновленного
    состояния из базы данных.
    """
    logger.info("Создается новая задача")
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    logger.info(f"Задача успешно создана (id={new_task.id})")
    return new_task


def delete_task_by_id(id: int, session: Session) -> Task:
    """
    Удалить задачу из базы данных по её ID.

    Аргументы:
        id: ID задачи, которую нужно удалить.
        session: Сессия базы данных, используемая для удаления задачи.

    Возвращает:
        Удаленный объект Task.

    Вызывает:
        Exception: Если задача с указанным ID не найдена.

    Эта функция удаляет задачу с данным ID из базы данных,
    фиксирует транзакцию для сохранения изменений и возвращает
    удаленный объект Task. Если задача не найдена, вызывается исключение.
    """
    logger.info(f"Попытка удалить задачу с id={id}")
    task = session.get(Task, id)
    if not task:
        logger.error(f"Задача с id={id} не найдена для удаления")
        raise Exception("User not found")
    session.delete(task)
    session.commit()
    logger.info(f"Задача с id={id} успешно удалена")
    return task


def delete_all_tasks(session: Session) -> None:
    """
    Удалить все задачи из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для выполнения удаления.

    Возвращает:
        None

    Эта функция удаляет все записи задач из базы данных
    посредством выполнения массовой операции удаления в таблице Task
    и фиксирует транзакцию для сохранения изменений.
    """
    logger.warning("Инициировано удаление всех задач")
    count = session.query(Task).delete()
    session.commit()
    logger.info(f"Удалено {count} задач")
