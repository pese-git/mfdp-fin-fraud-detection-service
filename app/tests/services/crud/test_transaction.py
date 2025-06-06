import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from src.models.fin_transaction import FinTransaction
from src.models.user import User
from src.services.crud.fin_transaction import (
    get_all_fin_transactions,
    get_fin_transaction_by_id,
    create_fin_transaction,
    delete_fin_trnsaction_by_id,
    delete_all_fin_transactions,
)

from tests.common.test_router_common import (
    session_fixture,
    secret_key_fixture,
    create_test_user_fixture,
    test_token_fixture,
    username_fixture,
    password_fixture,
    email_fixture,
)


def test_create_transaction(session: Session, test_user: User) -> None:
    new_transaction = FinTransaction(
        TransactionID=12345,
        TransactionDT=1710000000,
        TransactionAmt=100,
        ProductCD='W',
        card1=1111,
        card2=2222,
        card4='visa',
        isFraud=1,
        task_id=5,
    )

    created_transaction = create_fin_transaction(new_transaction, session)
    assert created_transaction is not None
    assert created_transaction.TransactionID is not None
    assert created_transaction.TransactionAmt == 100


def test_get_all_transactions(session: Session, test_user: User) -> None:
    transactions = [
        FinTransaction(
            TransactionID=12345,
            TransactionDT=1710000000,
            TransactionAmt=100,
            ProductCD='W',
            card1=1111,
            card2=2222,
            card4='visa',
            isFraud=1,
            task_id=5,
        ),
        FinTransaction(
            TransactionID=54321,
            TransactionDT=1710000000,
            TransactionAmt=200,
            ProductCD='W',
            card1=1111,
            card2=2222,
            card4='visa',
            isFraud=1,
            task_id=5,
        ),
    ]
    session.add_all(transactions)
    session.commit()

    retrieved_transactions = get_all_fin_transactions(session)
    assert len(retrieved_transactions) == 2
    assert all(isinstance(t, FinTransaction) for t in retrieved_transactions)


def test_get_transaction_by_id(session: Session, test_user: User) -> None:
    transaction = FinTransaction(
        TransactionID=12345,
        TransactionDT=1710000000,
        TransactionAmt=150,
        ProductCD='W',
        card1=1111,
        card2=2222,
        card4='visa',
        isFraud=1,
        task_id=5,
    )
    session.add(transaction)
    session.commit()

    retrieved_transaction = get_fin_transaction_by_id(transaction.id, session)
    assert retrieved_transaction is not None
    assert retrieved_transaction.id == transaction.id


def test_delete_transaction_by_id(session: Session, test_user: User) -> None:
    transaction = FinTransaction(
        TransactionID=12345,
        TransactionDT=1710000000,
        TransactionAmt=300,
        ProductCD='W',
        card1=1111,
        card2=2222,
        card4='visa',
        isFraud=1,
        task_id=5,
    )
    session.add(transaction)
    session.commit()

    deleted_transaction = delete_fin_trnsaction_by_id(transaction.id, session)
    assert deleted_transaction.id == transaction.id
    assert get_fin_transaction_by_id(transaction.id, session) is None


def test_delete_all_transactions(session: Session, test_user: User) -> None:
    session.add_all(
        [
            FinTransaction(
                TransactionID=12345,
                TransactionDT=1710000000,
                TransactionAmt=100,
                ProductCD='W',
                card1=1111,
                card2=2222,
                card4='visa',
                isFraud=1,
                task_id=5,
            ),
            FinTransaction(
                TransactionID=54321,
                TransactionDT=1710000000,
                TransactionAmt=200,
                ProductCD='W',
                card1=1111,
                card2=2222,
                card4='visa',
                isFraud=1,
                task_id=5,
            ),
        ]
    )
    session.commit()

    delete_all_fin_transactions(session)
    assert len(get_all_fin_transactions(session)) == 0
