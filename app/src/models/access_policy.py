from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class AccessPolicy(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    role_id: Optional[int] = Field(foreign_key="role.id")
    role: "Role" = Relationship(back_populates="access_policy")  # type: ignore # Роль, например, "admin", "user"

    resource: str = Field(nullable=False)  # Ресурс, например, "post", "comment"
    action: str = Field(
        nullable=False
    )  # Действие, например, "create", "read", "delete"
