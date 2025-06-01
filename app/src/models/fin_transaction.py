from typing import TYPE_CHECKING, Optional
from datetime import datetime
from click import Option
from sqlmodel import Field, Relationship, SQLModel
import sqlalchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Null, text
import sqlalchemy as sa

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

    C: Optional[list] = Field(
        sa_column=sqlalchemy.Column(JSONB, nullable=True), default=None,
    )
    D: Optional[list] = Field(
        sa_column=sqlalchemy.Column(JSONB, nullable=True), default=None,
    )
    M: Optional[list] = Field(
        sa_column=sqlalchemy.Column(JSONB, nullable=True), default=None,
    )
    V: Optional[list] = Field(
        sa_column=sqlalchemy.Column(JSONB, nullable=True), default=None,
    )
    IDs: Optional[list] = Field(
        sa_column=sqlalchemy.Column(JSONB, nullable=True), default=None,
    )

    isFraud: Optional[int] = Field(nullable=True, default=None)

    task_id: Optional[int] = Field(
        sa_column=sa.Column(sa.Integer, sa.ForeignKey("task.id", ondelete="CASCADE"))
    )
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