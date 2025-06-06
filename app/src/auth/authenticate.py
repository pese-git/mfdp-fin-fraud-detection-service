from typing import Any, Optional, cast
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session
from src.auth.cookieauth import OAuth2PasswordBearerWithCookie
from src.database.database import get_session
from src.auth.jwt_handler import verify_access_token
from src.services.crud.user import get_user_by_email

from src.database.config import get_settings

from src.services.logging.logging import get_logger

from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/oauth/signin")

oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(
    tokenUrl="/api/oauth/signin", auto_error=False
)


logger = get_logger(logger_name="auth")

def get_secret() -> str:
    key: str = get_settings().SECRET_KEY
    logger.debug("Получен SECRET_KEY для аутентификации")
    return key


def authenticate(
    token: str = Depends(oauth2_scheme), secret_key: str = Depends(get_secret)
) -> str:
    if not token:
        logger.warning("Попытка аутентификации без токена")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sign in for access"
        )
    try:
        decoded_token = verify_access_token(token, secret_key=secret_key)
        logger.info("Пользователь успешно аутентифицирован (user=%s)", decoded_token.get("user"))
        return cast(str, decoded_token["user"])
    except Exception as exc:
        logger.error("Неудачная аутентификация: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )


def authenticate_via_cookies(
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme_cookie),
    secret_key: str = Depends(get_secret),
) -> Optional[User]:
    if not token:
        logger.info("Попытка аутентификации через куки без токена")
        return None
    try:
        payload = verify_access_token(token, secret_key=secret_key)
        user_data: dict[str, Any] = payload.get("user")
        if user_data is None:
            logger.warning("Отсутствуют данные пользователя в токене (cookies)")
            return None
        logger.info("Пользователь успешно аутентифицирован через куки (email=%s)", user_data.get("email"))
        return get_user_by_email(email=user_data.get("email"), session=db)
    except Exception as exc:
        logger.error("Ошибка аутентификации через куки: %s", exc)
        return None


def get_current_user(
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
    secret_key: str = Depends(get_secret),
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_access_token(token, secret_key=secret_key)
        user_data: dict[str, Any] = payload.get("user")
        if user_data is None:
            logger.warning("Не найдены данные пользователя в токене при получении текущего пользователя")
            raise credentials_exception
    except JWTError as exc:
        logger.error("Ошибка JWT при получении текущего пользователя: %s", exc)
        raise credentials_exception
    user = get_user_by_email(email=user_data.get("email"), session=db)
    if user is None:
        logger.warning("Пользователь с email %s не найден", user_data.get("email"))
        raise credentials_exception
    logger.info("Текущий пользователь успешно получен (email=%s)", user_data.get("email"))
    return user


def get_current_user_via_cookies(
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme_cookie),
    secret_key: str = Depends(get_secret),
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_access_token(token, secret_key=secret_key)
        user_data: dict[str, Any] = payload.get("user")
        if user_data is None:
            logger.warning("Не найдены данные пользователя в токене (via cookies)")
            raise credentials_exception
    except JWTError as exc:
        logger.error("JWT ошибка при получении пользователя через куки: %s", exc)
        raise credentials_exception
    user = get_user_by_email(email=user_data.get("email"), session=db)
    if user is None:
        logger.warning("Пользователь с email %s не найден (via cookies)", user_data.get("email"))
        raise credentials_exception
    logger.info("Пользователь через куки успешно получен (email=%s)", user_data.get("email"))
    return user
