from fastapi.testclient import TestClient
from sqlmodel import Session
from fastapi import status

from src.models.wallet import Wallet
from common.test_router_common import (
    client_fixture,
    session_fixture,
    secret_key_fixture,
    create_test_user_fixture,
    test_token_fixture,
    username_fixture,
    password_fixture,
    email_fixture,
)


def test_retrieve_all_wallets(client: TestClient, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/wallet/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_wallet(client: TestClient, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    new_wallet_data = {"user_id": 1, "balance": 1000}
    response = client.post("/api/wallet/new", json=new_wallet_data, headers=headers)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["user_id"] == new_wallet_data["user_id"]
    assert response_data["balance"] == new_wallet_data["balance"]


def test_retrieve_wallet(client: TestClient, session: Session, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    # Создание кошелька для теста
    new_wallet = Wallet(user_id=1, balance=500)
    session.add(new_wallet)
    session.commit()
    response = client.get(f"/api/wallet/{new_wallet.id}", headers=headers)
    assert response.status_code == 200
    wallet_data = response.json()
    assert wallet_data["id"] == new_wallet.id
    assert wallet_data["balance"] == new_wallet.balance


def test_delete_wallet(client: TestClient, session: Session, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    # Создание кошелька для теста
    new_wallet = Wallet(user_id=1, balance=500)
    session.add(new_wallet)
    session.commit()
    response = client.delete(f"/api/wallet/{new_wallet.id}", headers=headers)
    assert response.status_code == 200
    assert session.get(Wallet, new_wallet.id) is None


def test_delete_all_wallets(
    client: TestClient, session: Session, test_token: str
) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    # Добавьте несколько кошельков для теста
    session.add(Wallet(user_id=1, balance=500))
    session.add(Wallet(user_id=2, balance=1000))
    session.commit()
    response = client.delete("/api/wallet/", headers=headers)
    assert response.status_code == 200
    assert session.query(Wallet).count() == 0
