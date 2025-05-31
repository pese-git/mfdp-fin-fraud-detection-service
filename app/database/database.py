# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy.orm import Session, sessionmaker
# from sqlalchemy import URL, create_engine, text
from sqlmodel import SQLModel, Session, create_engine 
from contextlib import contextmanager
from .config import get_settings

engine = create_engine(url=get_settings().DATABASE_URL_psycopg, 
                       echo=True, pool_size=5, max_overflow=10)

def get_session():
    with Session(engine) as session:
        yield session
        
def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
