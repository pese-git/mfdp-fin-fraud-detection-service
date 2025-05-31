from sqlmodel import Session
from src.models.wallet import Wallet
from typing import List, Optional


def get_all_wallets(session: Session) -> List[Wallet]:
    """
    Получить все записи кошельков из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для выполнения запроса.

    Возвращает:
        Список объектов Wallet, представляющих все записи кошельков в базе данных.
    """
    return session.query(Wallet).all()


def get_wallet_by_id(id: int, session: Session) -> Optional[Wallet]:
    """
    Получить запись кошелька по его ID.

    Аргументы:
        id: ID кошелька, который нужно получить.
        session: Сессия базы данных, используемая для выполнения запроса.

    Возвращает:
        Объект Wallet, если кошелек с указанным ID существует, в противном случае — None.
    """
    return session.get(Wallet, id)


def create_wallet(new_wallet: Wallet, session: Session) -> Wallet:
    """
    Добавить новый кошелек в базу данных.

    Аргументы:
        new_wallet: Объект Wallet, представляющий новый кошелек, который нужно добавить.
        session: Сессия базы данных, используемая для выполнения операции.

    Возвращает:
        Новый объект Wallet, обновленный с текущим состоянием из базы данных.
    """
    session.add(new_wallet)
    session.commit()
    session.refresh(new_wallet)
    return new_wallet


def delete_wallet_by_id(id: int, session: Session) -> Wallet:
    """
    Удалить запись кошелька по его ID.

    Аргументы:
        id: ID кошелька, который нужно удалить.
        session: Сессия базы данных, используемая для выполнения удаления.

    Вызывает:
        Exception: Если кошелек с указанным ID не найден.

    Возвращает:
        Объект Wallet, который был удален.
    """
    wallet = session.get(Wallet, id)
    if not wallet:
        raise Exception("User not found")
    # Удаляем кошелек
    session.delete(wallet)
    session.commit()
    return wallet


def delete_all_wallets(session: Session) -> None:
    """
    Удалить все записи кошельков из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для выполнения удаления.

    Возвращает:
        None
    """
    session.query(Wallet).delete()
    session.commit()
