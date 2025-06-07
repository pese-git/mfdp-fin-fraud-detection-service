from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas import Token, UserCreate, UserRead
from sqlmodel import Session
from src.auth.hash_password import HashPassword
from src.auth.jwt_handler import create_access_token
from src.database.config import get_settings
from src.database.database import get_session
from src.models.role import Role
from src.models.user import User
from src.services.crud import user as UserService
from src.services.logging.logging import get_logger


def get_secret_key() -> str | None:
    key = get_settings().SECRET_KEY
    return key


# Основной маршрут для работы с OAuth
oauth_route = APIRouter(tags=["OAuth"])
hash_password = HashPassword()


logger = get_logger(logger_name="oauth")


@oauth_route.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    response_description="Create a new user",
)
async def signup(data: UserCreate, session: Session = Depends(get_session)) -> UserRead:
    logger.info(f"Попытка регистрации пользователя: name={data.name}, email={data.email}")

    if UserService.get_user_by_email(data.email, session) is not None:
        logger.warning(f"Регистрация отклонена: email={data.email} уже существует")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied email already exists",
        )

    user_role = session.query(Role).filter_by(name="user").first()
    if not user_role:
        raise HTTPException(
            status_code=500,
            detail="Role 'user' not found. Please initialize roles in the database.",
        )

    new_user: User = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password.create_hash(data.password),
        role_id=user_role.id,
    )

    UserService.create_user(
        new_user,
        session,
    )
    logger.info(f"Успешная регистрация: id={new_user.id}, email={new_user.email}")

    return UserRead(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        is_active=new_user.is_active,
        # wallet=new_user.wallet,
        # transactions=[],
        # predictions=[],
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
    )


@oauth_route.post(
    "/signin",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    response_description="User login",
)
async def sign_user_in(
    user: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
    secret_key: str = Depends(get_secret_key),
) -> dict[str, Any]:
    logger.info(f"Попытка входа для пользователя: email={user.username}")
    user_exist = UserService.get_user_by_email(user.username, session)

    if user_exist is None:
        logger.warning(f"Вход отклонён: email={user.username} не найден")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    if user_exist.is_active is False:
        logger.warning(f"Вход отклонён: email={user.username} (id={user_exist.id}) не активен")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not active")

    if hash_password.verify_hash(user.password, user_exist.hashed_password):
        access_token = create_access_token(
            {
                "id": user_exist.id,
                "email": user_exist.email,
                "role": user_exist.roles.name,
            },
            secret_key=secret_key,
        )
        logger.info(f"Успешный вход: email={user_exist.email}, id={user_exist.id}")
        return {"access_token": access_token, "token_type": "Bearer"}

    logger.warning(f"Вход отклонён: неверный пароль для email={user.username}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid details passed.")
