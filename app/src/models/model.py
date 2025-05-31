from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, text


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

    tasks: Optional[List["Task"]] = Relationship(back_populates="model")  # type: ignore

    created_at: datetime = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
