from sqlalchemy.orm import Session
from src.models.access_policy import AccessPolicy


class AccessControl:
    def __init__(self, db: Session):
        self.db = db

    def can_access(self, role: str, resource: str, action: str) -> bool:
        """
        Проверяет, есть ли у роли разрешение на выполнение действия над ресурсом.
        """
        policy = (
            self.db.query(AccessPolicy)
            .filter_by(role=role, resource=resource, action=action)
            .first()
        )
        return policy is not None
