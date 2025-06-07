import pytest
from fastapi import HTTPException, status
from sqlmodel import Session
from src.auth.authenticate import (
    authenticate,
    authenticate_via_cookies,
    get_current_user,
)
from tests.common.test_router_common import *

# @pytest.fixture
# def create_test_user(session: Session):
#    user = User(name="Test User", email="test@example.com", hashed_password="hashedpassword", is_active=True, role_id=0)
#    create_user(user, session)  # Используем session_fixture на уровне вызова
#    return user
#
#
# @pytest.fixture
# def test_token(create_test_user, secret_key: str):
#    user_data = {"id": create_test_user.id, "email": create_test_user.email}
#    return create_access_token(user=user_data, secret_key=secret_key)


# def test_authenticate(test_token: str, secret_key: str, email: str) -> None:
#    user_info = authenticate(test_token, secret_key=secret_key)
#    print(user_info)
#    assert user_info == email


def test_authenticate_invalid_token(secret_key: str) -> None:
    invalid_token = "thisisnotavalidtoken"
    with pytest.raises(HTTPException, match="Invalid token") as excinfo:
        authenticate(invalid_token, secret_key=secret_key)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST


def test_authenticate_missing_token(secret_key: str) -> None:
    with pytest.raises(HTTPException) as excinfo:
        authenticate("", secret_key=secret_key)  # Используйте секретный ключ внутри
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail == "Sign in for access"


def test_get_current_user(session: Session, test_token: str, secret_key: str, email: str) -> None:
    user = get_current_user(session, test_token, secret_key=secret_key)
    assert user is not None
    assert user.email == email


def test_get_current_user_invalid_token(session: Session) -> None:
    invalid_token = "thisisnotavalidtoken"
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(session, invalid_token)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Invalid token"


def test_authenticate_via_cookies(session: Session, test_token: str, secret_key: str, email: str) -> None:
    user = authenticate_via_cookies(session, test_token, secret_key=secret_key)
    assert user is not None
    assert user.email == email


def test_authenticate_via_cookies_no_token(session: Session, secret_key: str) -> None:
    user = authenticate_via_cookies(session, "", secret_key=secret_key)
    assert user is None
