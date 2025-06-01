from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel, text

# Условный импорт для избежания циклических зависимостей
if TYPE_CHECKING:
    from models.task import Task
    
class Model(SQLModel, table=True):
    """
    Представляет модель базы данных с атрибутами для id, имени и пути.

    Атрибуты:
        id (int): Первичный ключ модели. Автоматически генерируется, если не предоставлено.
        name (str): Уникальное и не допускающее пустых значений имя для модели. Должно быть уникальным среди всех моделей.
        path (Optional[str]): Необязательный путь, связанный с моделью.

        tasks (Optional[List["Task"]]): Связь со списком объектов Task, которые ссылаются на эту модель.

        created_at (datetime): Временная метка, когда модель была создана.
                               По умолчанию установлено на текущую временную метку, установленную сервером.
        updated_at (datetime): Временная метка, когда модель была последней раз обновлена.
                               Автоматически устанавливается на текущую временную метку UTC, когда происходят изменения модели.
    """

    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    path: Optional[str]
    is_active: Optional[bool] = Field(default=False, nullable=False)

    tasks: Optional[List["Task"]] = Relationship(back_populates="model")  # type: ignore

    created_at: datetime = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
