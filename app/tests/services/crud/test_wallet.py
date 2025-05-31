import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from src.models.user import User
from src.models.wallet import Wallet
from src.services.crud.wallet import (
    get_all_wallets,
    get_wallet_by_id,
    create_wallet,
    delete_wallet_by_id,
    delete_all_wallets,
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


def test_create_wallet(session: Session, test_user: User) -> None:
    new_wallet = Wallet(user_id=test_user.id, balance=1000.0)
    created_wallet = create_wallet(new_wallet, session)
    assert created_wallet is not None
    assert created_wallet.id is not None
    assert created_wallet.balance == 1000.0


def test_get_all_wallets(session: Session, test_user: User) -> None:
    new_wallet_1 = Wallet(user_id=test_user.id, balance=1000.0)
    new_wallet_2 = Wallet(user_id=test_user.id, balance=1000.0)

    wallets = [new_wallet_1, new_wallet_2]
    session.add_all(wallets)
    session.commit()

    retrieved_wallets = get_all_wallets(session)
    assert len(retrieved_wallets) == 3
    for wallet, retrieved in zip(wallets, retrieved_wallets):
        assert wallet.balance == retrieved.balance


def test_get_wallet_by_id(session: Session) -> None:
    wallet = Wallet(user_id=1, balance=500.0)
    session.add(wallet)
    session.commit()

    retrieved_wallet = get_wallet_by_id(wallet.id, session)
    assert retrieved_wallet is not None
    assert retrieved_wallet.balance == wallet.balance


def test_delete_wallet_by_id(session: Session) -> None:
    wallet = Wallet(user_id=1, balance=300.0)
    session.add(wallet)
    session.commit()

    deleted_wallet = delete_wallet_by_id(wallet.id, session)
    assert deleted_wallet.id == wallet.id
    assert get_wallet_by_id(wallet.id, session) is None


def test_delete_all_wallets(session: Session) -> None:
    session.add_all([Wallet(user_id=i, balance=i * 200.0) for i in range(1, 4)])
    session.commit()

    delete_all_wallets(session)
    assert len(get_all_wallets(session)) == 0
