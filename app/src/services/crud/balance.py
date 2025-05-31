from typing import Any, Optional
from sqlalchemy import select
from sqlmodel import Session

from src.models.transaction import Transaction, TransactionType
from src.models.wallet import Wallet


def get_balance_by_user_id(user_id: int, session: Session) -> int:
    """
    Получает баланс кошелька пользователя по его ID.

    Аргументы:
        user_id (int): ID пользователя, баланс кошелька которого нужно получить.
        session (Session): Объект сессии SQLAlchemy, используемой для взаимодействия с базой данных.

    Возвращает:
        Optional[int]: Баланс кошелька пользователя, или None, если кошелек не найден.
    """
    wallet: Wallet = session.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise RuntimeError("Wallet is not create")

    return int(wallet.balance)


def update_balance_by_user_id(user_id: int, amount: int, session: Session) -> int:
    """
    Обновляет баланс кошелька пользователя по его ID. Также создается запись о транзакции.

    Аргументы:
        user_id (int): ID пользователя, баланс кошелька которого нужно обновить.
        amount (int): Сумма, которую следует добавить к балансу кошелька. Может быть положительной или отрицательной.
        session (Session): Объект сессии SQLAlchemy, используемой для взаимодействия с базой данных.

    Возвращает:
        dict: Сообщение, указывающее, что обновление баланса прошло успешно.

    Вызывает:
        Exception: Если кошелек не найден или возникает ошибка базы данных, будет выброшено исключение
                   с подробным сообщением.

    Эта функция выполняет следующие действия:
    1. Начинает транзакцию в базе данных.
    2. Получает кошелек пользователя по его ID.
    3. Обновляет баланс кошелька пользователя на указанную сумму.
    4. Создает новую запись о транзакции с указанной суммой и маркирует ее как доходную транзакцию.
    5. Фиксирует транзакцию, если ошибки не возникают.
    6. Откатывает транзакцию и выбрасывает исключение, если возникает ошибка.
    """
    try:
        # Запрос с возвратом объектов Wallet
        wallet = session.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            raise Exception("Not found wallet")

        # Обновляем баланс кошелька
        wallet.balance += amount

        print("#####################")
        print(f"## {wallet.balance}")
        print("#####################")

        if wallet.balance < 0:
            raise Exception("The balance cannot be below 0.")

        # Создаем запись о транзакции
        new_transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type=(
                TransactionType.INCOME if amount > 0 else TransactionType.EXPENSE
            ),
        )
        session.add(new_transaction)

        session.commit()

        return int(wallet.balance)

    except Exception as e:
        session.rollback()
        raise RuntimeError(str(e))
