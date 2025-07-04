from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

# Условный импорт для избежания циклических зависимостей
if TYPE_CHECKING:
    from models.access_policy import AccessPolicy
    from models.user import User


class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)  # Пример: "admin", "user"

    # user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="roles")
    # access_policy_id: Optional[int] = Field(foreign_key="accesspolicy.id")
    access_policy: Optional["AccessPolicy"] = Relationship(back_populates="role")
