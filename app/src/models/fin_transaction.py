"""Модель SQLModel для финансовых транзакций.

Данный модуль содержит определение модели FinTransaction, которая используется для хранения
и управления информацией о финансовых транзакциях в системе.
Модель поддерживает работу с различными свойствами транзакций (идентификаторы карт, адреса, суммы, домены email,
векторные признаки и пр.), а также связывает транзакцию с задачей (Task).
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

import sqlalchemy as sa
from sqlalchemy import text
from sqlmodel import Field, Relationship, SQLModel

# Условный импорт для избежания циклических зависимостей
if TYPE_CHECKING:
    from models.task import Task


class FinTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    TransactionID: int = Field(index=True)
    TransactionDT: int
    TransactionAmt: float
    ProductCD: str
    card1: Optional[int] = Field(default=None)
    card2: Optional[int] = Field(default=None)
    card3: Optional[float] = Field(default=None)
    card4: Optional[str] = Field(default=None)
    card5: Optional[float] = Field(default=None)
    card6: Optional[str] = Field(default=None)
    addr1: Optional[float] = Field(default=None)
    addr2: Optional[float] = Field(default=None)
    dist1: Optional[float] = Field(default=None)
    dist2: Optional[float] = Field(default=None)
    P_emaildomain: Optional[str] = Field(default=None)
    R_emaildomain: Optional[str] = Field(default=None)

    C: Optional[List[Any]] = Field(
        sa_column=sa.Column(sa.JSON, nullable=True),
        default=None,
    )
    D: Optional[List[Any]] = Field(
        sa_column=sa.Column(sa.JSON, nullable=True),
        default=None,
    )
    M: Optional[List[Any]] = Field(
        sa_column=sa.Column(sa.JSON, nullable=True),
        default=None,
    )
    V: Optional[List[Any]] = Field(
        sa_column=sa.Column(sa.JSON, nullable=True),
        default=None,
    )
    IDs: Optional[List[Any]] = Field(
        sa_column=sa.Column(sa.JSON, nullable=True),
        default=None,
    )

    isFraud: Optional[int] = Field(nullable=True, default=None)

    task_id: Optional[int] = Field(sa_column=sa.Column(sa.Integer, sa.ForeignKey("task.id", ondelete="CASCADE")))
    task: Optional["Task"] = Relationship(back_populates="fintransaction")

    created_at: datetime = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
