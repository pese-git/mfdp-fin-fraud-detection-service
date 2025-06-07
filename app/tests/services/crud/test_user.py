from sqlmodel import Session
from src.models.role import Role
from src.models.user import User
from src.services.crud.user import (
    create_user,
    delete_all_users,
    delete_user_by_id,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    get_user_by_name,
)
from tests.common.test_router_common import *

# from src.models.transaction import Transaction, TransactionType


def test_create_user(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)

    new_user = User(
        name="New User",
        email="newuser@example.com",
        hashed_password="hashedpassword",
        role_id=user_role.id,
    )
    created_user = create_user(new_user, session)
    assert created_user is not None
    assert created_user.id is not None
    assert created_user.name == "New User"


def test_get_user_by_id(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
    user = User(
        name="Test User",
        email="user@example.com",
        hashed_password="hashedpassword",
        role_id=user_role.id,
    )
    session.add(user)
    session.commit()

    retrieved_user = get_user_by_id(user.id, session)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id


def test_get_user_by_email(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
    user = User(
        name="Another User",
        email="another@example.com",
        hashed_password="hashedpassword",
        role_id=user_role.id,
    )
    session.add(user)
    session.commit()

    retrieved_user = get_user_by_email("another@example.com", session)
    assert retrieved_user is not None
    assert retrieved_user.email == "another@example.com"


def test_get_user_by_name(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
    user = User(
        name="Special User",
        email="special@example.com",
        hashed_password="hashedpassword",
        role_id=user_role.id,
    )
    session.add(user)
    session.commit()

    retrieved_user = get_user_by_name("Special User", session)
    assert retrieved_user is not None
    assert retrieved_user.name == "Special User"


def test_delete_user_by_id(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
    user = User(
        name="Delete User",
        email="delete@example.com",
        hashed_password="hashedpassword",
        role_id=user_role.id,
    )
    session.add(user)
    session.commit()

    deleted_user = delete_user_by_id(user.id, session)
    assert deleted_user.id == user.id
    assert get_user_by_id(user.id, session) is None


def test_delete_all_users(session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
    session.add(
        User(
            name="User One",
            email="one@example.com",
            hashed_password="hashed1",
            role_id=user_role.id,
        )
    )
    session.add(
        User(
            name="User Two",
            email="two@example.com",
            hashed_password="hashed2",
            role_id=user_role.id,
        )
    )
    session.commit()

    delete_all_users(session)
    assert len(get_all_users(session)) == 0
