import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from src.models.transaction import Transaction, TransactionType
from src.models.user import User
from src.services.crud.transaction import (
    get_all_transactions,
    get_transaction_by_id,
    create_transaction,
    delete_transaction_by_id,
    delete_all_transactions,
)

from common.test_router_common import (
    session_fixture,
    secret_key_fixture,
    create_test_user_fixture,
    test_token_fixture,
    username_fixture,
    password_fixture,
    email_fixture,
)


def test_create_transaction(session: Session, test_user: User) -> None:
    new_transaction = Transaction(
        amount=100, transaction_type=TransactionType.INCOME, user_id=test_user.id
    )
    created_transaction = create_transaction(new_transaction, session)
    assert created_transaction is not None
    assert created_transaction.id is not None
    assert created_transaction.amount == 100


def test_get_all_transactions(session: Session, test_user: User) -> None:
    transactions = [
        Transaction(
            amount=100, transaction_type=TransactionType.INCOME, user_id=test_user.id
        ),
        Transaction(
            amount=200, transaction_type=TransactionType.EXPENSE, user_id=test_user.id
        ),
    ]
    session.add_all(transactions)
    session.commit()

    retrieved_transactions = get_all_transactions(session)
    assert len(retrieved_transactions) == 2
    assert all(isinstance(t, Transaction) for t in retrieved_transactions)


def test_get_transaction_by_id(session: Session, test_user: User) -> None:
    transaction = Transaction(
        amount=150, transaction_type=TransactionType.INCOME, user_id=test_user.id
    )
    session.add(transaction)
    session.commit()

    retrieved_transaction = get_transaction_by_id(transaction.id, session)
    assert retrieved_transaction is not None
    assert retrieved_transaction.id == transaction.id


def test_delete_transaction_by_id(session: Session, test_user: User) -> None:
    transaction = Transaction(
        amount=300, transaction_type=TransactionType.EXPENSE, user_id=test_user.id
    )
    session.add(transaction)
    session.commit()

    deleted_transaction = delete_transaction_by_id(transaction.id, session)
    assert deleted_transaction.id == transaction.id
    assert get_transaction_by_id(transaction.id, session) is None


def test_delete_all_transactions(session: Session, test_user: User) -> None:
    session.add_all(
        [
            Transaction(
                amount=100,
                transaction_type=TransactionType.INCOME,
                user_id=test_user.id,
            ),
            Transaction(
                amount=200,
                transaction_type=TransactionType.EXPENSE,
                user_id=test_user.id,
            ),
        ]
    )
    session.commit()

    delete_all_transactions(session)
    assert len(get_all_transactions(session)) == 0
