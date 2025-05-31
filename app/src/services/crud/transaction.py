from sqlmodel import Session
from src.models.transaction import Transaction
from typing import List, Optional


def get_all_transactions(session: Session) -> List[Transaction]:
    """
    Получить все транзакции из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для выполнения запроса.

    Возвращает:
        Список объектов Transaction, представляющих все транзакции в базе данных.
    """
    return session.query(Transaction).all()


def get_transaction_by_id(id: int, session: Session) -> Optional[Transaction]:
    """
    Получить транзакцию из базы данных по её ID.

    Аргументы:
        id (int): ID транзакции, которую нужно получить.
        session: Сессия базы данных, используемая для выполнения запроса.

    Возвращает:
        Optional[Transaction]: Объект Transaction, если транзакция с указанным ID найдена, в противном случае — None.
    """
    return session.get(Transaction, id)


def create_transaction(new_transaction: Transaction, session: Session) -> Transaction:
    """
    Добавить новую транзакцию в базу данных и зафиксировать изменения.

    Аргументы:
        new_transaction (Transaction): Объект транзакции, который будет добавлен в базу данных.
        session: Сессия базы данных, используемая для выполнения операции.

    Возвращает:
        None
    """
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)
    return new_transaction


def delete_transaction_by_id(id: int, session: Session) -> Transaction:
    """
    Удалить экземпляр транзакции из базы данных по ее ID.

    :param id: Уникальный идентификатор транзакции, которую нужно удалить.
    :param session: Сессия базы данных, используемая для выполнения операции.
    :return: Экземпляр Transaction, который был удален.
    :raises Exception: Если Transaction с указанным ID не найдена.
    """
    transaction = session.get(Transaction, id)
    if not transaction:
        raise Exception("User not found")
    # Удаляем модель
    session.delete(transaction)
    session.commit()
    return transaction


def delete_all_transactions(session: Session) -> None:
    """
    Удалить все экземпляры транзакций из базы данных.

    :param session: Сессия базы данных, используемая для выполнения операции.
    :return: None
    """
    session.query(Transaction).delete()
    session.commit()
