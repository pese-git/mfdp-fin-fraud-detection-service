from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.fin_transaction import FinTransaction
from src.models.user import User
from tests.common.test_router_common import *


def test_retrieve_all_transactions(client: TestClient, session: Session, test_token: str) -> None:
    # user, password = create_test_user(session)
    # access_token = get_access_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/transaction/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_retrieve_transaction(client: TestClient, session: Session, test_user: User, test_token: str) -> None:
    # user, password = create_test_user(session)
    # access_token = get_access_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {test_token}"}
    new_transaction = FinTransaction(
        TransactionID=12345,
        TransactionDT=1710000000,
        TransactionAmt=100.50,
        ProductCD="W",
        card1=1111,
        card2=2222,
        card4="visa",
        isFraud=1,
        task_id=5,
    )
    session.add(new_transaction)
    session.commit()
    response = client.get(f"/api/transaction/{new_transaction.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    transaction_data = response.json()
    assert transaction_data["TransactionAmt"] == new_transaction.TransactionAmt
    assert transaction_data["TransactionDT"] == new_transaction.TransactionDT


def test_delete_transaction(client: TestClient, session: Session, test_user: User, test_token: str) -> None:
    # user, password = create_test_user(session)
    # access_token = get_access_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {test_token}"}
    new_transaction = FinTransaction(
        TransactionID=12345,
        TransactionDT=1710000000,
        TransactionAmt=100.50,
        ProductCD="W",
        card1=1111,
        card2=2222,
        card4="visa",
        isFraud=1,
        task_id=5,
    )
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)

    response = client.delete(f"/api/transaction/{new_transaction.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert session.get(FinTransaction, new_transaction.id) is None


def test_delete_all_transactions(client: TestClient, session: Session, test_user: User, test_token: str) -> None:
    # user, password = create_test_user(session)
    # access_token = get_access_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {test_token}"}
    session.add(
        FinTransaction(
            TransactionID=12345,
            TransactionDT=1710000000,
            TransactionAmt=100.50,
            ProductCD="W",
            card1=1111,
            card2=2222,
            card4="visa",
            isFraud=1,
            task_id=5,
        )
    )
    session.add(
        FinTransaction(
            TransactionID=5431,
            TransactionDT=1710000000,
            TransactionAmt=200.50,
            ProductCD="W",
            card1=1111,
            card2=2222,
            card4="visa",
            isFraud=1,
            task_id=5,
        )
    )
    session.commit()

    response = client.delete("/api/transaction/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert session.query(FinTransaction).count() == 0
