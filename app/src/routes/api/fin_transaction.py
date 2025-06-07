from typing import Any, List, cast

import src.services.crud.fin_transaction as FinTransactionService
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.fin_transaction import FinTransaction
from src.services.logging.logging import get_logger

fin_transaction_router = APIRouter(tags=["Transaction"])


logger = get_logger(logger_name="api.fin_transaction")


@fin_transaction_router.get("/", response_model=List[FinTransaction])
async def retrieve_all_transactions(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> List[FinTransaction]:
    logger.info(
        "Пользователь '%s' (id=%s) запрашивает все транзакции.",
        user.get("name"),
        user.get("id"),
    )
    transactions = FinTransactionService.get_all_fin_transactions(session=session)
    logger.debug("Получено транзакций: %d", len(transactions))
    return cast(List[FinTransaction], transactions)


@fin_transaction_router.get("/{id}", response_model=FinTransaction)
async def retrieve_transaction(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> FinTransaction:
    logger.info(
        "Пользователь '%s' (id=%s) запрашивает транзакцию id=%s.",
        user.get("name"),
        user.get("id"),
        id,
    )
    transaction = FinTransactionService.get_fin_transaction_by_id(id, session=session)
    if not transaction:
        logger.warning("Транзакция id=%s не найдена.", id)
        raise HTTPException(status_code=404, detail=f"Transaction {id} not found")
    logger.debug("Транзакция id=%s найдена.", id)
    return transaction


@fin_transaction_router.delete("/{id}", response_model=FinTransaction)
async def delete_transaction(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> FinTransaction:
    logger.info(
        "Пользователь '%s' (id=%s) удаляет транзакцию id=%s.",
        user.get("name"),
        user.get("id"),
        id,
    )
    try:
        deleted = FinTransactionService.delete_fin_trnsaction_by_id(id, session=session)
        logger.info("Транзакция id=%s успешно удалена.", id)
        return deleted
    except Exception as e:
        logger.exception("Ошибка при удалении транзакции id=%s: %s", id, str(e))
        raise


@fin_transaction_router.delete("/")
async def delete_all_transactions(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> dict[str, Any]:
    logger.warning(
        "Пользователь '%s' (id=%s) удаляет ВСЕ транзакции!",
        user.get("name"),
        user.get("id"),
    )
    try:
        FinTransactionService.delete_all_fin_transactions(session=session)
        logger.info("Все транзакции успешно удалены.")
        return {"message": "Предсказания удалены успешно"}
    except Exception as e:
        logger.exception("Ошибка при удалении всех транзакций: %s", str(e))
        return {"message": "Ошибка при удалении всех предсказаний"}
