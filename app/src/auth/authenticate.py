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

from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/oauth/signin")

oauth2_scheme_cookie = OAuth2PasswordBearerWithCookie(
    tokenUrl="/api/oauth/signin", auto_error=False
)


def get_secret() -> str:
    key: str = get_settings().SECRET_KEY
    return key


def authenticate(
    token: str = Depends(oauth2_scheme), secret_key: str = Depends(get_secret)
) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sign in for access"
        )
    try:
        decoded_token = verify_access_token(token, secret_key=secret_key)
        return cast(str, decoded_token["user"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )


def authenticate_via_cookies(
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme_cookie),
    secret_key: str = Depends(get_secret),
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = verify_access_token(token, secret_key=secret_key)
        user_data: dict[str, Any] = payload.get("user")
        if user_data is None:
            return None
        return get_user_by_email(email=user_data.get("email"), session=db)
    except Exception:
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
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(email=user_data.get("email"), session=db)
    if user is None:
        raise credentials_exception
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
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(email=user_data.get("email"), session=db)
    if user is None:
        raise credentials_exception
    return user
