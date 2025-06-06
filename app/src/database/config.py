from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from src.services.logging.logging import get_logger


logger = get_logger(logger_name="database.config")

load_dotenv()


class Settings(BaseSettings):
    """
    Класс настроек Pydantic для загрузки и управления переменными окружения,
    связанными с конфигурациями подключения к базе данных.

    Атрибуты:
        DB_HOST (Optional[str]): Имя хоста сервера базы данных.
        DB_PORT (Optional[int]): Номер порта, на котором слушает сервер базы данных.
        DB_USER (Optional[str]): Имя пользователя для аутентификации с базой данных.
        DB_PASS (Optional[str]): Пароль для пользователя базы данных.
        DB_NAME (Optional[str]): Имя базы данных, к которой нужно подключиться.

    Свойства:
        DATABASE_URL_asyncpg (str): Создает URL подключения для asyncpg.
        DATABASE_URL_psycopg (str): Создает URL подключения для psycopg.

    Конфигурация:
        env_file (str): Путь к файлу .env, из которого загружаются переменные окружения.
        env_file_encoding (str): Кодировка, используемая для файла .env.
        extra (str): Определяет, что делать с дополнительными полями, не определенными в модели.

    Функции:
        get_settings() -> Settings:
            Возвращает кешированный экземпляр класса Settings.
    """

    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_QUEUE: Optional[str] = None
    RABBITMQ_DEFAULT_USER: Optional[str] = None
    RABBITMQ_DEFAULT_PASS: Optional[str] = None

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        url = f"postgresql+asyncpg://{self.DB_USER}:{'***' if self.DB_PASS else None}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        logger.debug("Сформирован DATABASE_URL_asyncpg: %s", url)
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self) -> str:
        url = f"postgresql+psycopg://{self.DB_USER}:{'***' if self.DB_PASS else None}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        logger.debug("Сформирован DATABASE_URL_psycopg: %s", url)
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Разрешить дополнительные поля, не указанные в модели


@lru_cache()
def get_settings() -> Settings:
    logger.info("Загрузка настроек из переменных окружения")
    settings = Settings()
    logger.info("Настройки успешно загружены: DB_HOST=%s, DB_PORT=%s, DB_USER=%s, DB_NAME=%s", 
                settings.DB_HOST, settings.DB_PORT, settings.DB_USER, settings.DB_NAME)
    return settings
