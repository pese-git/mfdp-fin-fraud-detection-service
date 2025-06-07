import time
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from src.services.logging.logging import get_logger

logger = get_logger(logger_name="auth.jwt_handler")


def create_access_token(user: dict[str, Any], secret_key: str) -> str:
    logger.debug("Создание access_token для пользователя: %s", user.get("email", "unknown"))
    payload = {"user": user, "expires": time.time() + 3600}
    token: str = jwt.encode(payload, secret_key, algorithm="HS256")
    logger.info("Access_token успешно создан (user=%s)", user.get("email", "unknown"))
    return token


def verify_access_token(token: str, secret_key: str) -> dict[str, Any]:
    logger.debug("Попытка верификации access_token")
    try:
        data: dict[str, Any] = jwt.decode(token, secret_key, algorithms=["HS256"])
        expire = data.get("expires")
        if expire is None:
            logger.error("В access_token отсутствует поле 'expires'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            logger.warning("Токен истёк")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token expired!")
        logger.info(
            "Access_token успешно верифицирован для пользователя: %s",
            data["user"].get("email", "unknown") if "user" in data else "unknown",
        )
        return data
    except JWTError as exc:
        logger.error("Неуспешная верификация access_token: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token") from exc
