from datetime import datetime
from enum import Enum
from sqlmodel import Relationship, SQLModel, Field, text
from typing import Optional
import sqlalchemy as sa


class TransactionType(str, Enum):
    """Перечисление, представляющее тип транзакции.

    Атрибуты:
        INCOME (str): Представляет доходную транзакцию.
        EXPENSE (str): Представляет расходную транзакцию.
    """

    INCOME = "income"
    EXPENSE = "expense"


class Transaction(SQLModel, table=True):
    """
    Представляет запись финансовой транзакции в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор транзакции.
                  Это автоматически увеличивающийся первичный ключ.

        amount (int): Денежная сумма транзакции.
        transaction_type (TransactionType): Тип транзакции,
                                            либо 'income' (доход), либо 'expense' (расход).
        user_id (Optional[int]): Внешний ключ, ссылающийся на ID связанного пользователя.
                                 Может быть необязательным и иметь значение None.
        user (Optional["User"]): Пользователь, связанный с транзакцией.
                                 Это отношение позволяет получить доступ к пользователю
                                 через транзакцию и является обратно заполняемым
                                 из транзакций пользователя.
        created_at (datetime): Временная метка, когда была создана транзакция.
                               По умолчанию устанавливается на текущую временную метку и не может быть пустой.
    """

    id: int = Field(default=None, primary_key=True)
    amount: int

    transaction_type: TransactionType

    user_id: Optional[int] = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="transactions")  # type: ignore

    task_id: Optional[int] = Field(
        sa_column=sa.Column(sa.Integer, sa.ForeignKey("task.id", ondelete="CASCADE"))
    )
    task: Optional["Task"] = Relationship(back_populates="transaction")  # type: ignore

    created_at: datetime = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
