from typing import cast

from passlib.context import CryptContext
from src.services.logging.logging import get_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = get_logger(logger_name="auth.hash_password")


class HashPassword:
    def create_hash(self, password: str) -> str:
        logger.debug("Вызван метод create_hash для генерации пароля")
        return cast(str, pwd_context.hash(password))

    def verify_hash(self, plain_password: str, hashed_password: str) -> bool:
        logger.debug("Вызван метод verify_hash для проверки пароля")
        try:
            result = cast(bool, pwd_context.verify(plain_password, hashed_password))
            if result:
                logger.info("Успешная верификация пароля")
            else:
                logger.warning("Неуспешная верификация пароля")
            return result
        except Exception as exc:
            logger.error("Ошибка при проверке хэша пароля: %s", exc)
            return False
