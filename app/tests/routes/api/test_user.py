from fastapi.testclient import TestClient
from sqlmodel import Session
from fastapi import status

from src.models.role import Role
from src.models.user import User
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


def test_retrieve_profile(client: TestClient, test_user: User, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}

    # Проверим профиль
    response = client.get("/api/user/profile", headers=headers)
    assert response.status_code == 200
    profile_data = response.json()
    assert profile_data["name"] == test_user.name
    assert profile_data["email"] == test_user.email


def test_create_user(client: TestClient, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}

    user_data = {
        "name": "New User",
        "email": "newuser@example.com",
        "hashed_password": "newpassword",
    }
    response = client.post("/api/user/new", json=user_data, headers=headers)
    assert response.status_code == 201
    created_user = response.json()
    assert created_user["name"] == user_data["name"]
    assert created_user["email"] == user_data["email"]


def test_read_users(client: TestClient, session: Session, test_token: str) -> None:
    # Добавьте нескольких пользователей
    user_role: Role = session.query(Role).filter_by(name="user").first()

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

    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/user/", headers=headers)
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 3


def test_delete_user(
    client: TestClient, session: Session, test_token: str, test_user: User
) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    user = User(
        name="User One",
        email="one@example.com",
        hashed_password="hashed1",
        roles=user_role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.delete(f"/api/user/{user.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert session.get(User, user.id) is None


def test_delete_all_users(
    client: TestClient, session: Session, test_token: str, test_user: User
) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}

    # Добавьте нескольких пользователей
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

    response = client.delete("/api/user/", headers=headers)
    assert response.status_code == 200
    assert session.query(User).count() == 0
