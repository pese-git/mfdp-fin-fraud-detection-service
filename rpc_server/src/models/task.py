from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel, text

# Условный импорт для избежания циклических зависимостей
if TYPE_CHECKING:
    from models.model import Model
    from models.fin_transaction import FinTransaction
    
class Task(SQLModel, table=True):
    """
    Представляет сущность задачи в приложении на основе SQLModel.

    Объект Task соответствует записи в таблице базы данных с тем же именем.
    Он включает следующие поля:

    Атрибуты:
        id (int): Первичный ключ задачи, автоматически генерируется, если не предоставлен.

        model_id (Optional[int]): Внешний ключ, ссылающийся на таблицу Model. Этот атрибут
                                  может быть None, если задача не связана с конкретной моделью.

        model (Optional["Model"]): Атрибут отношения, который ссылается на связанный
                                   объект Model. Использует возможности отношений SQLModel
                                   для установления двусторонней связи с "tasks" в качестве
                                   идентификатора back_populates на стороне Model.

        prediction (Optional["Prediction"]): Атрибут отношения, который ссылается на связанный
                                             объект Prediction. Это форма другой стороны
                                             отношения типа один-к-одному или один-ко-многим,
                                             с "task" в качестве идентификатора back_populates
                                             на стороне Prediction.

        created_at (datetime): Временная метка, обозначающая, когда задача была создана. Это поле
                               автоматически устанавливается на текущую временную метку базой данных
                               с использованием `CURRENT_TIMESTAMP` в SQL и не может быть пустым.
    """

    id: int = Field(default=None, primary_key=True)
    task_id: str

    status: str

    model_id: Optional[int] = Field(default=None, foreign_key="model.id")
    model: Optional["Model"] = Relationship(back_populates="tasks")

    #prediction: Optional["Prediction"] = Relationship(back_populates="task")
    fintransaction: Optional[List["FinTransaction"]] = Relationship(back_populates="task")  # type: ignore

    created_at: datetime = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )

    model_config = {"protected_namespaces": ()}  # Отключает защиту
