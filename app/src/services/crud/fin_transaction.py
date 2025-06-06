from sqlmodel import Session
from src.models.fin_transaction import FinTransaction
#from src.models.prediction import Prediction
from typing import List, Optional


def get_all_fin_transaction(session: Session) -> List[FinTransaction]:
    """
    Получить все записи предсказаний из базы данных.

    Эта функция выполняет запрос к сессии базы данных для всех экземпляров модели Prediction
    и возвращает их в списке. Она предполагает, что предоставленная сессия правильно настроена
    для взаимодействия с базой данных, и что модель Prediction корректно определена.

    Аргументы:
        session: Сессия базы данных, используемая для выполнения запроса модели Prediction.

    Возвращает:
        List[Prediction]: Список, содержащий все экземпляры Prediction из базы данных.
    """
    return session.query(FinTransaction).all()


def get_fin_transaction_by_id(id: int, session: Session) -> Optional[FinTransaction]:
    """
    Получить запись предсказания по его ID.

    Эта функция пытается получить запись Prediction из базы данных, используя
    предоставленный ID. Если запись существует, она возвращается; иначе возвращается None.

    Аргументы:
        id (int): Уникальный идентификатор предсказания, которое нужно получить.
        session: Сессия базы данных, используемая для выполнения запроса модели Prediction.

    Возвращает:
        Optional[Prediction]: Экземпляр Prediction, если найден, в противном случае — None.
    """
    transaction = session.get(FinTransaction, id)
    if transaction:
        return transaction
    return None


def create_fin_transaction(new_transaction: FinTransaction, session: Session) -> FinTransaction:
    """
    Добавить новую запись предсказания в базу данных.

    Эта функция добавляет новый экземпляр модели Prediction в базу данных
    с использованием предоставленной сессии. Она фиксирует изменения для сохранения записи
    в базе данных и обновляет состояние вновь добавленного
    экземпляра для отражения любых изменений, внесенных в процессе фиксации.

    Аргументы:
        new_wallet (Prediction): Экземпляр Prediction, который будет добавлен в базу данных.
        session: Сессия базы данных, используемая для добавления и фиксации экземпляра Prediction.

    Возвращает:
        None
    """
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)
    return new_transaction


def delete_fin_trnsaction_by_id(id: int, session: Session) -> FinTransaction:
    """
    Удалить запись предсказания по его ID.

    Эта функция пытается получить запись Prediction из базы данных, используя
    предоставленный ID. Если запись существует, она удаляется из базы данных.
    Если запись не существует, возникает исключение.
    Изменения фиксируются в базе данных, и удаленный экземпляр Prediction
    возвращается.

    Аргументы:
        id (int): Уникальный идентификатор предсказания, которое нужно удалить.
        session: Сессия базы данных, используемая для выполнения запроса и удаления модели Prediction.

    Возвращает:
        Prediction: Экземпляр Prediction, который был удален из базы данных.

    Вызывает:
        Exception: Если Prediction с указанным ID не найден.
    """
    predict = session.get(FinTransaction, id)
    if not predict:
        raise Exception("User not found")
    # Удаляем предсказание
    session.delete(predict)
    session.commit()
    return predict


def delete_all_fin_transactions(session: Session) -> None:
    """
    Удалить все записи предсказаний из базы данных.

    Эта функция удаляет все экземпляры модели Prediction из базы данных
    с использованием предоставленной сессии. Она фиксирует изменения, чтобы гарантировать, что все
    записи удалены из базы данных навсегда.

    Аргументы:
        session: Сессия базы данных, используемая для удаления и фиксации экземпляров Prediction.

    Возвращает:
        None
    """
    session.query(FinTransaction).delete()
    session.commit()
