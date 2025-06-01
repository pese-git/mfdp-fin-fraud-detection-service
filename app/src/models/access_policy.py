from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

# Условный импорт для избежания циклических зависимостей
if TYPE_CHECKING:
    from models.role import Role
    
class AccessPolicy(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    role_id: Optional[int] = Field(foreign_key="role.id")
    role: "Role" = Relationship(back_populates="access_policy")  # Роль, например, "admin", "user"

    resource: str = Field(nullable=False)  # Ресурс, например, "post", "comment"
    action: str = Field(
        nullable=False
    )  # Действие, например, "create", "read", "delete"
