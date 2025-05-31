from fastapi import APIRouter, Body, HTTPException, status, Depends
from sqlmodel import Session
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.wallet import Wallet
import src.services.crud.wallet as WalletService
from typing import List

wallet_router = APIRouter(tags=["Wallet"])


@wallet_router.get("/", response_model=List[Wallet], status_code=status.HTTP_200_OK)
async def retrieve_all_wallets(
    session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> List[Wallet]:
    """
    Получить список всех кошельков.

    Возвращает:
        Список объектов Wallet, представляющих все кошельки в базе данных.
    """
    return WalletService.get_all_wallets(session=session)


@wallet_router.get("/{id}", response_model=Wallet, status_code=status.HTTP_200_OK)
async def retrieve_wallet(
    id: int, session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> Wallet:
    """
    Получить кошелек по его ID.

    Аргументы:
        id: Идентификатор кошелька, который нужно получить.

    Возвращает:
        Объект Wallet, представляющий найденный кошелек.

    Исключения:
        HTTPException: Если кошелек с указанным ID не найден.
    """
    wallet = WalletService.get_wallet_by_id(id, session=session)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )
    return wallet


@wallet_router.post("/new", response_model=Wallet, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    body: Wallet = Body(...),
    session: Session = Depends(get_session),
    user: dict = Depends(authenticate),
) -> Wallet:
    """
    Создать новый кошелек.

    Аргументы:
        body: Данные кошелька, который будет создан.

    Возвращает:
        Созданный объект Wallet.
    """
    new_wallet = WalletService.create_wallet(body, session=session)
    return new_wallet


@wallet_router.delete("/{id}", response_model=Wallet, status_code=status.HTTP_200_OK)
async def delete_wallet(
    id: int, session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> Wallet:
    """
    Удалить кошелек по его ID.

    Аргументы:
        id: Идентификатор кошелька, который нужно удалить.

    Возвращает:
        Объект Wallet, который был удален.

    Исключения:
        HTTPException: Если кошелек с указанным ID не найден.
    """
    wallet = WalletService.delete_wallet_by_id(id, session=session)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )
    return wallet


@wallet_router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_wallets(
    session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> dict:
    """
    Удалить все кошельки из базы данных.

    Возвращает:
        Сообщение об успешном удалении всех кошельков.
    """
    WalletService.delete_all_wallets(session=session)
    return {"message": "Wallets deleted successfully"}
