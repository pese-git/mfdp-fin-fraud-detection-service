from sqlmodel import Session
from src.models.task import Task
from typing import List, Optional


def get_all_tasks(session: Session) -> List[Task]:
    """
    Получить все задачи из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для выполнения запроса задач.

    Возвращает:
        Список объектов Task, представляющих все задачи в базе данных.
    """
    return session.query(Task).all()


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
    return session.get(Task, id)


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
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
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
    task = session.get(Task, id)
    if not task:
        raise Exception("User not found")
    # Удаляем задачу
    session.delete(task)
    session.commit()
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
    session.query(Task).delete()
    session.commit()
