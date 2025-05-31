from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Relationship, SQLModel, Field, text
from typing import Optional, List


class User(SQLModel, table=True):
    """
    Представляет пользователя в базе данных с связанными атрибутами и связями.

    Атрибуты:
        id (int): Первичный ключ, уникальный идентификатор для каждого пользователя.
        name (str): Имя пользователя.
        email (str): Уникальный адрес электронной почты пользователя, не может быть пустым.
        hashed_password (str): Пароль для аккаунта пользователя.

        transactions (Optional[List["Transaction"]]): Список транзакций, связанных с пользователем.
        predictions (Optional[List["Prediction"]]): Список предсказаний, связанных с пользователем.

        wallet (Optional["Wallet"]): Кошелек, связанный с пользователем.
                                     Поддерживает каскадное удаление.

        created_at (datetime): Временная метка, когда пользователь был создан, автоматически генерируется базой данных.
        updated_at (datetime): Временная метка, когда пользователь был последним раз обновлен, управляется автоматически.
    """

    id: int = Field(default=None, primary_key=True)
    name: str
    email: EmailStr = Field(unique=True, nullable=False)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)

    transactions: Optional[List["Transaction"]] = Relationship(back_populates="user")  # type: ignore
    predictions: Optional[List["Prediction"]] = Relationship(back_populates="user")  # type: ignore

    wallet: Optional["Wallet"] = Relationship(back_populates="user", cascade_delete=True)  # type: ignore

    created_at: datetime = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
