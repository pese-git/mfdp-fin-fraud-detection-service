# Модель предсказаний
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, text
import sqlalchemy as sa


class Prediction(SQLModel, table=True):
    """
    Представляет запись предсказания в базе данных.

    Атрибуты:
        id (int): Первичный ключ записи предсказания.
        input_data (str): Входные данные, используемые для создания предсказания.
        result (str): Результат предсказания.
        user_id (int): Внешний ключ, ссылающийся на пользователя, который создал предсказание.
        user (Optional["User"]): Объект пользователя, связанный с этим предсказанием, определяющий связь обратно к списку предсказаний пользователя.
        task_id (Optional[int]): Внешний ключ, ссылающийся на задачу, связанную с этим предсказанием, если таковая имеется, с поведением каскадного удаления.
        task (Optional["Task"]): Объект задачи, связанный с этим предсказанием, определяющий связь обратно к предсказанию в задаче.
        created_at (datetime): Временная метка, когда предсказание было создано, автоматически устанавливается базой данных на текущую временную метку.
    """

    id: int = Field(default=None, primary_key=True)

    input_data: str
    result: str

    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="predictions")  # type: ignore

    task_id: Optional[int] = Field(
        sa_column=sa.Column(sa.Integer, sa.ForeignKey("task.id", ondelete="CASCADE"))
    )
    task: Optional["Task"] = Relationship(back_populates="prediction")  # type: ignore

    created_at: datetime = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
