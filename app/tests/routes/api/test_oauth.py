import uuid

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.auth.hash_password import HashPassword
from src.models.role import Role
from src.models.user import User
from tests.common.test_router_common import *


def test_signup(client: TestClient, test_user: User) -> None:
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
    }
    response = client.post("/api/oauth/signup", json=user_data)
    assert response.status_code == 201
    # assert response.json() == {"message": "User successfully registered!"}


def test_signup_invalid(client: TestClient) -> None:
    invalid_email = "demo{}@example@com".format(uuid.uuid4())
    response = client.post(
        "/api/oauth/signup",
        json={"name": "demo", "email": invalid_email, "password": "demo"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_existing_user(client: TestClient, session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
    hashed_password = HashPassword().create_hash("testpassword")
    existing_user = User(
        name="Existing User",
        email="existing@example.com",
        hashed_password=hashed_password,
        role_id=user_role.id,
    )
    session.add(existing_user)
    session.commit()

    user_data = {
        "name": "New User",
        "email": "existing@example.com",
        "password": "newpassword",
    }
    response = client.post("/api/oauth/signup", json=user_data)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with supplied email already exists"}


def test_signin(client: TestClient, session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
    hashed_password = HashPassword().create_hash("testpassword")
    user = User(
        name="Test User",
        email="signin@example.com",
        hashed_password=hashed_password,
        role_id=user_role.id,
    )
    session.add(user)
    session.commit()

    response = client.post(
        "/api/oauth/signin",
        data={"username": "signin@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "Bearer"


def test_signin_invalid_user(client: TestClient) -> None:
    response = client.post(
        "/api/oauth/signin",
        data={"username": "nonexistent@example.com", "password": "testpassword"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User does not exist"}


def test_signin_invalid_password(client: TestClient, session: Session, test_user: User) -> None:
    user_role = session.query(Role).filter_by(name="user").first()
    if user_role is None:
        user_role = Role(name="user")
        session.add(user_role)
        session.commit()
        session.refresh(user_role)
    user = User(
        name="Another User",
        email="valid@example.com",
        hashed_password=HashPassword().create_hash("rightpassword"),
        role_id=user_role.id,
    )
    session.add(user)
    session.commit()

    response = client.post(
        "/api/oauth/signin",
        data={"username": "valid@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid details passed."}
