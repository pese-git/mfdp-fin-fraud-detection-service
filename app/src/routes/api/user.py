from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import Session
from src.auth.hash_password import HashPassword
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.user import User
from src.models.role import Role
import src.services.crud.user as UserService
from typing import List, Optional
from src.services.logging.logging import get_logger



user_router = APIRouter(tags=["User"])


logger = get_logger(logger_name="user_router")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str | None = None
    created_at: datetime

    updated_at: datetime


@user_router.get(
    "/profile", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def retrieve_profile(
    session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> UserResponse:
    logger.info(f"Пользователь id={user.get('id', '[Unknown]')} запрашивает свой профиль")
    db_user = UserService.get_user_by_id(user["id"], session=session)
    if not db_user:
        logger.warning(f"Профиль пользователя id={user.get('id', '[Unknown]')} не найден")
    else:
        logger.debug(f"Профиль пользователя id={user['id']} найден: {db_user}")
    return db_user


@user_router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def retrieve_all_users(
    session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> List[UserResponse]:
    logger.info(f"Пользователь id={user.get('id', '[Unknown]')} получает список всех пользователей")
    try:
        users = UserService.get_all_users(session=session)
        logger.info(f"Найдено пользователей: {len(users)}")
        return users
    except Exception as e:
        logger.error(f"Ошибка при получении всех пользователей: {e}", exc_info=True)
        raise


@user_router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def retrieve_user(
    id: int, session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> UserResponse:
    logger.info(f"Пользователь id={user.get('id', '[Unknown]')} получает пользователя id={id}")
    db_user = UserService.get_user_by_id(id, session=session)
    if not db_user:
        logger.warning(f"Пользователь с id={id} не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    logger.debug(f"Пользователь id={id} найден: {db_user}")
    return db_user


@user_router.post(
    "/new", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    body: User = Body(...),
    session: Session = Depends(get_session),
    user: dict = Depends(authenticate),
) -> UserResponse:
    logger.info(f"Пользователь id={user.get('id', '[Unknown]')} создает нового пользователя (email={body.email})")
    try:
        user_role: Role = session.query(Role).filter_by(name="user").first()

        body.hashed_password = HashPassword().create_hash(body.hashed_password)
        body.role_id = user_role.id

        new_user = UserService.create_user(body, session=session)
        logger.info(f"Новый пользователь id={new_user.id} (email={new_user.email}) успешно создан")
        return new_user
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя email={body.email}: {e}", exc_info=True)
        raise


@user_router.delete(
    "/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def delete_user(
    id: int, session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> UserResponse:
    logger.info(f"Пользователь id={user.get('id', '[Unknown]')} удаляет пользователя id={id}")
    db_user = UserService.delete_user_by_id(id, session=session)
    if not db_user:
        logger.warning(f"Пользователь id={id} для удаления не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    logger.info(f"Пользователь id={id} успешно удален")
    return db_user


@user_router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_users(
    session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> dict:
    logger.warning(f"Пользователь id={user.get('id', '[Unknown]')} инициирует удаление всех пользователей!")
    try:
        UserService.delete_all_users(session=session)
        logger.info("Все пользователи успешно удалены")
        return {"message": "Users deleted successfully"}
    except Exception as e:
        logger.error(f"Ошибка при удалении всех пользователей: {e}", exc_info=True)
        raise
