# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy.orm import Session, sessionmaker
# from sqlalchemy import URL, create_engine, text
from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from contextlib import contextmanager
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
