import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session
from fastapi import status

from src.models.fin_transaction import FinTransaction

from tests.common.test_router_common import (
    client_fixture,
    session_fixture,
    secret_key_fixture,
    create_test_user_fixture,
    test_token_fixture,
    username_fixture,
    password_fixture,
    email_fixture,
)
from src.models.user import User


def test_retrieve_all_transactions(
    client: TestClient, session: Session, test_token: str
) -> None:
    # user, password = create_test_user(session)
    # access_token = get_access_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/transaction/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


#def test_create_transaction(
#    client: TestClient, session: Session, test_user: User, test_token: str
#) -> None:
#    # user, password = create_test_user(session)
#    # access_token = get_access_token(client, user.email, password)
#    headers = {"Authorization": f"Bearer {test_token}"}
#    new_transaction_data = {
#        "amount": 100,
#        "transaction_type": "income",
#        "user_id": test_user.id,
#    }
#    response = client.post(
#        "/api/transaction/new", json=new_transaction_data, headers=headers
#    )
#
#    assert response.status_code == status.HTTP_201_CREATED
#    response_data = response.json()
#
#    assert response_data["amount"] == new_transaction_data["amount"]
#    assert response_data["transaction_type"] == new_transaction_data["transaction_type"]


def test_retrieve_transaction(
    client: TestClient, session: Session, test_user: User, test_token: str
) -> None:
    # user, password = create_test_user(session)
    # access_token = get_access_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {test_token}"}
    new_transaction = FinTransaction(
        TransactionID=12345,
        TransactionDT=1710000000,
        TransactionAmt=100.50,
        ProductCD='W',
        card1=1111,
        card2=2222,
        card4='visa',
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


def test_delete_transaction(
    client: TestClient, session: Session, test_user: User, test_token: str
) -> None:
    # user, password = create_test_user(session)
    # access_token = get_access_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {test_token}"}
    new_transaction = FinTransaction(
        TransactionID=12345,
        TransactionDT=1710000000,
        TransactionAmt=100.50,
        ProductCD='W',
        card1=1111,
        card2=2222,
        card4='visa',
        isFraud=1,
        task_id=5,
    )
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)

    response = client.delete(f"/api/transaction/{new_transaction.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert session.get(FinTransaction, new_transaction.id) is None


def test_delete_all_transactions(
    client: TestClient, session: Session, test_user: User, test_token: str
) -> None:
    # user, password = create_test_user(session)
    # access_token = get_access_token(client, user.email, password)
    headers = {"Authorization": f"Bearer {test_token}"}
    session.add(
        FinTransaction(
            TransactionID=12345,
            TransactionDT=1710000000,
            TransactionAmt=100.50,
            ProductCD='W',
            card1=1111,
            card2=2222,
            card4='visa',
            isFraud=1,
            task_id=5,
        )
    )
    session.add(
        FinTransaction(
            TransactionID=5431,
            TransactionDT=1710000000,
            TransactionAmt=200.50,
            ProductCD='W',
            card1=1111,
            card2=2222,
            card4='visa',
            isFraud=1,
            task_id=5,
        )
    )
    session.commit()

    response = client.delete("/api/transaction/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert session.query(FinTransaction).count() == 0
