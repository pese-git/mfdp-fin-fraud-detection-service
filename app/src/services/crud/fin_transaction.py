# from src.models.prediction import Prediction
from typing import List, Optional

from sqlmodel import Session
from src.models.fin_transaction import FinTransaction
from src.services.logging.logging import get_logger

logger = get_logger(logger_name="FinTransactionCRUD")


def get_all_fin_transactions(session: Session) -> List[FinTransaction]:
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
    logger.info("Запрошен список всех финансовых транзакций")
    transactions = session.query(FinTransaction).all()
    logger.debug(f"Найдено {len(transactions)} транзакций")
    return transactions


def get_fin_transaction_by_id(
    id: int | None, session: Session
) -> Optional[FinTransaction]:
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
    logger.info(f"Запрошена финансовая транзакция по id={id}")
    transaction = session.get(FinTransaction, id)
    if transaction:
        logger.debug(f"Транзакция с id={id} найдена")
        return transaction
    logger.warning(f"Транзакция с id={id} не найдена")
    return None


def create_fin_transaction(
    new_transaction: FinTransaction, session: Session
) -> FinTransaction:
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
    logger.info("Создается новая финансовая транзакция")
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)
    logger.info(f"Транзакция успешно создана (id={new_transaction.id})")
    return new_transaction


def delete_fin_trnsaction_by_id(id: int | None, session: Session) -> FinTransaction:
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
    logger.info(f"Попытка удалить фин. транзакцию с id={id}")
    predict = session.get(FinTransaction, id)
    if not predict:
        logger.error(f"Транзакция с id={id} не найдена для удаления")
        raise Exception("User not found")
    session.delete(predict)
    session.commit()
    logger.info(f"Транзакция с id={id} успешно удалена")
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
    logger.warning("Инициировано удаление всех финансовых транзакций")
    count = session.query(FinTransaction).delete()
    session.commit()
    logger.info(f"Удалено {count} транзакций")
