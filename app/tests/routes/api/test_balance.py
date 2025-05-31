from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session
from fastapi import status

from src.models.user import User
from src.models.wallet import Wallet

from src.services.crud.balance import get_balance_by_user_id

from common.test_router_common import (
    client_fixture,
    session_fixture,
    secret_key_fixture,
    create_test_user_fixture,
    test_token_fixture,
    username_fixture,
    password_fixture,
    email_fixture,
    initial_balance_fixture,
)


def test_deposit_balance(
    session: Session,
    client: TestClient,
    test_user: User,
    test_token: str,
    initial_balance: int,
) -> None:
    deposit_amount = 500
    response = client.post(
        f"/api/balance/{test_user.id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"amount": deposit_amount},
    )

    assert response.status_code == 200, response.text
    # Проверяем, что баланс увеличился на сумму депозита
    updated_balance = get_balance_by_user_id(test_user.id, session=session)
    assert updated_balance == initial_balance + deposit_amount


def test_withdraw_balance(
    session: Session,
    client: TestClient,
    test_user: User,
    test_token: str,
    initial_balance: int,
) -> None:
    withdraw_amount = 200.0
    response = client.post(
        f"/api/balance/{test_user.id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"amount": -withdraw_amount},
    )

    assert response.status_code == 200, response.text
    # Проверяем, что баланс уменьшился на сумму вывода
    updated_balance = get_balance_by_user_id(test_user.id, session=session)
    assert updated_balance == initial_balance - withdraw_amount


def test_withdraw_overdraft(
    client: TestClient, test_user: User, test_token: str, initial_balance: int
) -> None:
    overdraft_amount = initial_balance + 1200.0
    response = client.post(
        f"/api/balance/{test_user.id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"amount": -overdraft_amount},
    )

    # Ожидается ошибка из-за попытки списания превышающего лимит баланса
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error_message = response.json().get("detail")
    assert error_message == "The balance cannot be below 0."


def create_test_user_with_balance(user: User, session: Session) -> int:
    user_id = user.id  # Предположим, что пользователь с ID 1 существует
    wallet = Wallet(user_id=user_id, balance=100.0)
    session.add(wallet)
    session.commit()
    return user_id


def test_get_balance(
    client: TestClient,
    session: Session,
    test_token: str,
    test_user: User,
    initial_balance: int,
) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    user_id = create_test_user_with_balance(test_user, session)
    response = client.get(f"/api/balance/{user_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    balance_data = response.json()
    assert balance_data["balance"] == initial_balance
