# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy.orm import Session, sessionmaker
# from sqlalchemy import URL, create_engine, text
import sqlalchemy
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
from .config import get_settings


engine = create_engine(
    url=get_settings().DATABASE_URL_psycopg, echo=True, pool_size=5, max_overflow=10
)


def get_session() -> Generator[Session, None, None]:
    """
    Функция-генератор, которая предоставляет сессию SQLAlchemy, ограниченную контекстным менеджером.

    Эта функция использует глобальный движок SQLAlchemy для создания сессии.
    Она гарантирует, что ресурсы надлежащим образом управляются, предоставляя экземпляр сессии,
    который может быть использован для взаимодействия с базой данных в пределах оператора `with`.
    Сессия автоматически закрывается после выхода из блока, в котором она используется.

    Возвращает:
        Session: Экземпляр класса Session из SQLAlchemy, связанный с глобальным движком.
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Инициализирует базу данных путем удаления всех существующих таблиц и последующего
    их воссоздания на основе текущей метаданных SQLModel.

    Эта функция использует движок для подключения к базе данных и выполнения полной
    разборки и настройки схемы базы данных. Обычно она используется во время
    разработки или тестирования, чтобы гарантировать, что схема базы данных синхронизирована с
    определенными моделями.

    Примечание:
        Все существующие данные будут утеряны из-за операции 'drop_all'. Используйте эту
        функцию с осторожностью в производственных средах.
    """
    inspector = sqlalchemy.inspect(engine)
    existing_tables = inspector.get_table_names()
    # Проверяем, есть ли уже существующие таблицы
    if not existing_tables:
        print(f"Creating tables {existing_tables}")
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
    else:
        print("Tables already exist. No need to recreate them.")
