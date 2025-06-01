from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
from src.auth.jwt_handler import create_access_token
from src.auth.hash_password import HashPassword
from src.database.database import get_session
from src.models.user import User
from src.models.role import Role
from src.services.crud import user as UserService

from src.database.config import get_settings


def get_secret_key() -> str | None:
    key: str = get_settings().SECRET_KEY
    return key


class UserBase(BaseModel):
    name: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str | None = None
    #transactions: Optional[List[Transaction]]
    #predictions: Optional[List[Prediction]]
    #wallet: Optional[Wallet]
    created_at: datetime

    updated_at: datetime


# Основной маршрут для работы с OAuth
oauth_route = APIRouter(tags=["OAuth"])
hash_password = HashPassword()


@oauth_route.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Create a new user",
)
async def signup(
    data: UserBase, session: Session = Depends(get_session)
) -> UserResponse:
    """
    Регистрация нового пользователя в системе.

    - **email**: Электронная почта пользователя.
    - **password**: Пароль пользователя.

    Возвращает JSON-структуру с сообщением об успешной регистрации.
    """
    if UserService.get_user_by_email(data.email, session) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied email already exists",
        )



    user_role: Role = session.query(Role).filter_by(name="user").first()
    new_user: User = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password.create_hash(data.password),
        roles=user_role,
    )

    UserService.create_user(
        new_user,
        session,
    )
    return UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        #wallet=new_user.wallet,
        transactions=[],
        #predictions=[],
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
    )


@oauth_route.post(
    "/signin",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    response_description="User login",
)
async def sign_user_in(
    user: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
    secret_key: str = Depends(get_secret_key),
) -> dict[str, Any]:
    user_exist = UserService.get_user_by_email(user.username, session)

    if user_exist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    if user_exist.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User does not active"
        )

    if hash_password.verify_hash(user.password, user_exist.hashed_password):
        access_token = create_access_token(
            {
                "id": user_exist.id,
                "email": user_exist.email,
                "role": user_exist.roles.name,
            },
            secret_key=secret_key,
        )
        return {"access_token": access_token, "token_type": "Bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid details passed."
    )
