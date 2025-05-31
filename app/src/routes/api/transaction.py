from fastapi import APIRouter, Body, HTTPException, status, Depends
from sqlmodel import Session
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.transaction import Transaction
import src.services.crud.transaction as TransactionService
from typing import Any, List
from typing import cast

transaction_router = APIRouter(tags=["Transaction"])


@transaction_router.get(
    "/", response_model=List[Transaction], status_code=status.HTTP_200_OK
)
async def retrieve_all_transactions(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> List[Transaction]:
    """
    Получить все транзакции из базы данных.

    Возвращает:
        Список объектов Transaction, представляющих все транзакции в базе данных.
    """
    return cast(
        List[Transaction], TransactionService.get_all_transactions(session=session)
    )


@transaction_router.get(
    "/{id}", response_model=Transaction, status_code=status.HTTP_200_OK
)
async def retrieve_transaction(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Transaction:
    """
    Получить транзакцию по ее ID.

    Аргументы:
        id: Идентификатор транзакции для получения.

    Возвращает:
        Объект Transaction, соответствующий заданному ID.

    Исключения:
        HTTPException: Если транзакция с указанным ID не найдена.
    """
    transaction = TransactionService.get_transaction_by_id(id, session=session)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction with specified ID does not exist",
        )
    return transaction


@transaction_router.post(
    "/new", response_model=Transaction, status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    body: Transaction = Body(...),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Transaction:
    """
    Создать новую транзакцию в базе данных.

    Аргументы:
        body: Данные новой транзакции, которые необходимо добавить.

    Возвращает:
        Созданный объект Transaction.
    """
    new_transaction = TransactionService.create_transaction(body, session=session)
    return new_transaction


@transaction_router.delete(
    "/{id}", response_model=Transaction, status_code=status.HTTP_200_OK
)
async def delete_transaction(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Transaction:
    """
    Удалить транзакцию по ее ID.

    Аргументы:
        id: Идентификатор транзакции, которую нужно удалить.

    Возвращает:
        Сообщение о успешном удалении транзакции.

    Исключения:
        HTTPException: Если транзакция с указанным ID не найдена.
    """
    transaction = TransactionService.delete_transaction_by_id(id, session=session)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction with specified ID does not exist",
        )
    return transaction


@transaction_router.delete(
    "/", response_model=dict[str, Any], status_code=status.HTTP_200_OK
)
async def delete_all_transactions(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> dict[str, Any]:
    """
    Удалить все транзакции из базы данных.

    Возвращает:
        Сообщение об успешном удалении всех транзакций.
    """
    TransactionService.delete_all_transactions(session=session)
    return {"message": "Transactions deleted successfully"}
