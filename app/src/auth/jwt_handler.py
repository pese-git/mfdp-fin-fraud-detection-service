import time
from datetime import datetime
from typing import Any
from fastapi import HTTPException, status
from jose import jwt, JWTError


def create_access_token(user: dict[str, Any], secret_key: str) -> str:
    payload = {"user": user, "expires": time.time() + 3600}
    token: str = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def verify_access_token(token: str, secret_key: str) -> dict[str, Any]:
    try:
        data: dict[str, Any] = jwt.decode(token, secret_key, algorithms=["HS256"])
        expire = data.get("expires")
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token expired!"
            )
        return data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
