# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy.orm import Session, sessionmaker
# from sqlalchemy import URL, create_engine, text
import sqlalchemy
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
from .config import get_settings
from src.services.logging.logging import get_logger

logger = get_logger(logger_name="database")

engine = create_engine(
    url=get_settings().DATABASE_URL_psycopg, echo=False, pool_size=5, max_overflow=10
)
logger.info("Создан SQLAlchemy engine для %s", get_settings().DATABASE_URL_psycopg)


def get_session() -> Generator[Session, None, None]:
    """
    Функция-генератор, которая предоставляет сессию SQLAlchemy, ограниченную контекстным менеджером.
    """
    logger.debug("Открытие новой сессии БД")
    try:
        with Session(engine) as session:
            yield session
        logger.debug("Сессия БД успешно закрыта")
    except Exception as exc:
        logger.error("Ошибка при работе с сессией БД: %s", exc)
        raise


def init_db() -> None:
    """
    Инициализирует базу данных путем удаления всех существующих таблиц и последующего
    их воссоздания на основе текущей метаданных SQLModel.
    """
    logger.info("Инициализация базы данных...")
    inspector = sqlalchemy.inspect(engine)
    existing_tables = inspector.get_table_names()
    logger.debug("Существующие таблицы в базе: %s", existing_tables)
    if not existing_tables:
        logger.info("Таблицы отсутствуют. Создание таблиц заново.")
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        logger.info("Таблицы успешно созданы.")
    else:
        logger.info("Таблицы уже существуют. Воссоздание не требуется.")
