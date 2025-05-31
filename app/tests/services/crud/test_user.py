import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from src.models.role import Role
from src.models.user import User
from src.models.wallet import Wallet
from src.models.transaction import Transaction, TransactionType
from src.models.task import Task
from src.models.model import Model
from src.models.prediction import Prediction

from src.services.crud.user import (
    get_all_users,
    get_user_by_id,
    get_user_by_email,
    get_user_by_name,
    create_user,
    delete_user_by_id,
    delete_all_users,
)
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


def test_create_user(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    new_user = User(
        name="New User",
        email="newuser@example.com",
        hashed_password="hashedpassword",
        roles=user_role,
    )
    created_user = create_user(new_user, session)
    assert created_user is not None
    assert created_user.id is not None
    assert created_user.name == "New User"


def test_get_user_by_id(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    user = User(
        name="Test User",
        email="user@example.com",
        hashed_password="hashedpassword",
        roles=user_role,
    )
    session.add(user)
    session.commit()

    retrieved_user = get_user_by_id(user.id, session)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id


def test_get_user_by_email(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    user = User(
        name="Another User",
        email="another@example.com",
        hashed_password="hashedpassword",
        roles=user_role,
    )
    session.add(user)
    session.commit()

    retrieved_user = get_user_by_email("another@example.com", session)
    assert retrieved_user is not None
    assert retrieved_user.email == "another@example.com"


def test_get_user_by_name(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    user = User(
        name="Special User",
        email="special@example.com",
        hashed_password="hashedpassword",
        roles=user_role,
    )
    session.add(user)
    session.commit()

    retrieved_user = get_user_by_name("Special User", session)
    assert retrieved_user is not None
    assert retrieved_user.name == "Special User"


def test_delete_user_by_id(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    user = User(
        name="Delete User",
        email="delete@example.com",
        hashed_password="hashedpassword",
        roles=user_role,
    )
    session.add(user)
    session.commit()

    deleted_user = delete_user_by_id(user.id, session)
    assert deleted_user.id == user.id
    assert get_user_by_id(user.id, session) is None


def test_delete_all_users(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    session.add(
        User(
            name="User One",
            email="one@example.com",
            hashed_password="hashed1",
            roles=user_role,
        )
    )
    session.add(
        User(
            name="User Two",
            email="two@example.com",
            hashed_password="hashed2",
            roles=user_role,
        )
    )
    session.commit()

    delete_all_users(session)
    assert len(get_all_users(session)) == 0
