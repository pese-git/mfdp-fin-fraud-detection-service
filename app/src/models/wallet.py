from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, text
import sqlalchemy as sa


class Wallet(SQLModel, table=True):
    """
    Представляет сущность Кошелек в базе данных.

    Атрибуты:
        id (int): Первичный ключ и уникальный идентификатор кошелька.
        balance (int): Текущий баланс кошелька.

        user_id (int): Внешний ключ, ссылающийся на идентификатор связанного пользователя.
        user (Optional["User"]): Связь с сущностью Пользователь, указывающая владельца кошелька.

        created_at (datetime): Временная метка, когда кошелек был создан. Автоматически устанавливается базой данных.
        updated_at (datetime): Временная метка, когда кошелек был последним раз обновлен. Автоматически обновляется с текущим временем при модификации.
    """

    id: int = Field(default=None, primary_key=True)
    balance: int

    user_id: int = Field(
        sa_column=sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"))
    )
    user: Optional["User"] = Relationship(back_populates="wallet")  # type: ignore

    created_at: datetime = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
