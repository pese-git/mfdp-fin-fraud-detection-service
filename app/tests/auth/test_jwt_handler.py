from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt
from src.auth.jwt_handler import create_access_token, verify_access_token
from tests.common.test_router_common import *  # [wildcard-import]

# Сделаем временную SECRET_KEY для теста
SECRET_KEY = "testsecretkey"


def test_create_access_token() -> None:
    user_data = {"id": 123, "name": "testuser"}
    token = create_access_token(user=user_data, secret_key=SECRET_KEY)

    assert token is not None

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    assert decoded_token["user"]["id"] == 123
    assert decoded_token["user"]["name"] == "testuser"
    assert "expires" in decoded_token


def test_verify_access_token() -> None:
    user_data = {"id": 123, "name": "testuser"}
    token = create_access_token(user=user_data, secret_key=SECRET_KEY)

    # Должно быть успешно
    verified_data = verify_access_token(token, secret_key=SECRET_KEY)
    assert verified_data["user"]["id"] == 123


def test_expired_token() -> None:
    # Использование специального метода для создания сетевого токена
    user_data = {"id": 123, "name": "testuser"}
    expired_payload = {
        "user": user_data,
        "expires": (datetime.utcnow() - timedelta(seconds=10)).timestamp(),
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")

    with pytest.raises(HTTPException) as excinfo:
        verify_access_token(expired_token, secret_key=SECRET_KEY)

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Token expired!"


def test_invalid_token() -> None:
    invalid_token = "thisisnotatoken"

    with pytest.raises(HTTPException) as excinfo:
        verify_access_token(invalid_token, secret_key=SECRET_KEY)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Invalid token"
