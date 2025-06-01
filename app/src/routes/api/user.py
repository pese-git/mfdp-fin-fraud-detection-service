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

user_router = APIRouter(tags=["User"])
users = []


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
    user = UserService.get_user_by_id(user["id"], session=session)
    return user


@user_router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def retrieve_all_users(
    session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> List[UserResponse]:
    """
    Получить список всех пользователей.

    Возвращает:
        Список объектов User, представляющих всех пользователей в базе данных.
    """
    return UserService.get_all_users(session=session)


@user_router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def retrieve_user(
    id: int, session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> UserResponse:
    """
    Получить пользователя по его ID.

    Аргументы:
        id: Идентификатор пользователя, которого нужно получить.

    Возвращает:
        Объект User, представляющий найденного пользователя.

    Исключения:
        HTTPException: Если пользователь с указанным ID не найден.
    """
    user = UserService.get_user_by_id(id, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@user_router.post(
    "/new", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    body: User = Body(...),
    session: Session = Depends(get_session),
    user: dict = Depends(authenticate),
) -> UserResponse:
    """
    Создать нового пользователя и связанный с ним кошелек.

    Аргументы:
        body: Данные пользователя, который будет создан.

    Возвращает:
        Созданный объект User.
    """
    user_role: Role = session.query(Role).filter_by(name="user").first()

    body.hashed_password = HashPassword().create_hash(body.hashed_password)
    body.role_id = user_role.id

    new_user = UserService.create_user(body, session=session)
    return new_user


@user_router.delete(
    "/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def delete_user(
    id: int, session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> UserResponse:
    """
    Удалить пользователя по его ID.

    Аргументы:
        id: Идентификатор пользователя, которого нужно удалить.

    Возвращает:
        Объект User, который был удален.

    Исключения:
        HTTPException: Если пользователь с указанным ID не найден.
    """
    user = UserService.delete_user_by_id(id, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@user_router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_users(
    session: Session = Depends(get_session), user: dict = Depends(authenticate)
) -> dict:
    """
    Удалить всех пользователей из базы данных.

    Возвращает:
        Сообщение об успешном удалении всех пользователей.
    """
    UserService.delete_all_users(session=session)
    return {"message": "Users deleted successfully"}
