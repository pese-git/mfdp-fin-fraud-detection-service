from typing import Any
from typing import cast
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from src.auth.authenticate import authenticate
from src.database.database import get_session

from src.services.crud.balance import get_balance_by_user_id, update_balance_by_user_id


class BalanceResponse(BaseModel):
    message: str
    balance: int


class BalanceUpdate(BaseModel):
    amount: float


balance_router = APIRouter(tags=["Balance"])


# Получение баланса пользователя
@balance_router.get(
    "/{user_id}",
    response_model=BalanceResponse,
    description="Получить баланс для конкретного пользователя.",
)
def get_balance(
    user_id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> BalanceResponse:
    """
    Получить баланс для конкретного пользователя.

    Эта функция использует GET-запрос для получения баланса, связанного с указанным ID пользователя.
    Она использует зависимость от сессии базы данных для взаимодействия с базой данных и
    получения баланса для заданного пользователя.

    :param user_id: Целое число, представляющее ID пользователя, баланс которого нужно получить.
    :param session: Сессия базы данных, предоставленная функцией Depends(get_session).
    :return: Словарь, содержащий баланс пользователя.
    """
    balance = get_balance_by_user_id(user_id, session)
    return BalanceResponse(balance=balance, message="")


@balance_router.post(
    "/{user_id}",
    response_model=BalanceResponse,
    description="Обновить баланс для конкретного пользователя.",
)
def update_balance(
    user_id: int,
    update: BalanceUpdate,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> BalanceResponse:
    """
    Обновить баланс для конкретного пользователя.

    Эта функция обрабатывает POST-запросы для обновления баланса для указанного ID пользователя.
    Она получает необходимые данные из тела запроса, используя модель BalanceUpdate,
    и взаимодействует с базой данных для изменения баланса пользователя соответствующим образом.

    :param user_id: Целое число, представляющее ID пользователя, баланс которого нужно обновить.
    :param update: Экземпляр BalanceUpdate, содержащий новую сумму баланса для применения.
    :param session: Сессия базы данных, предоставленная функцией Depends(get_session), используемая
                    для выполнения операций с базой данных.
    """
    try:
        balance = update_balance_by_user_id(
            user_id=user_id, amount=update.amount, session=session
        )
        return BalanceResponse(balance=balance, message="")
    except RuntimeError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
