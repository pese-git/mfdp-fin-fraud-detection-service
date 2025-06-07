from sqlalchemy.orm import Session
from src.models.access_policy import AccessPolicy
from src.services.logging.logging import get_logger

# Инициализация логгера для этого модуля
logger = get_logger(logger_name="permission.access_control")


class AccessControl:
    def __init__(self, db: Session):
        self.db = db

    def can_access(self, role: str, resource: str, action: str) -> bool:
        """
        Проверяет, есть ли у роли разрешение на выполнение действия над ресурсом.
        """
        # Пробуем найти политику доступа
        policy = self.db.query(AccessPolicy).filter_by(role=role, resource=resource, action=action).first()
        if policy:
            # Логируем успешный допуск
            logger.debug(
                "Доступ РАЗРЕШЁН: роль='%s', ресурс='%s', действие='%s'",
                role,
                resource,
                action,
            )
        else:
            # Логируем отказ в доступе
            logger.warning(
                "Доступ ЗАПРЕЩЁН: роль='%s', ресурс='%s', действие='%s'",
                role,
                resource,
                action,
            )
        return policy is not None
