from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from src.app import app
from src.auth.hash_password import HashPassword
from src.auth.jwt_handler import create_access_token
from src.database.config import get_settings
from src.database.database import get_session
from src.models.role import Role
from src.models.user import User
from src.services.crud.user import create_user


@pytest.fixture(name="secret_key")
def secret_key_fixture() -> str | None:
    return get_settings().SECRET_KEY


@pytest.fixture(name="username")
def username_fixture() -> str:
    return "demo"


@pytest.fixture(name="password")
def password_fixture() -> str:
    return "demo"


@pytest.fixture(name="email")
def email_fixture() -> str:
    return "demo@demo.com"


@pytest.fixture(name="initial_balance")
def initial_balance_fixture() -> int:
    return 1000


@pytest.fixture(name="admin_role")
def admin_role_fixture(session: Session) -> Role:
    admin_role = Role(name="admin")
    user_role = Role(name="admiusern")
    session.add_all([admin_role, user_role])
    session.commit()

    return admin_role


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def create_test_user_fixture(session: Session, username: str, email: str, password: str) -> User:
    admin_role = Role(name="admin")
    user_role = Role(name="user")
    session.add_all([admin_role, user_role])
    session.commit()

    hashed_password = HashPassword().create_hash(password)
    user = User(
        name=username,
        email=email,
        hashed_password=hashed_password,
        role_id=admin_role.id,
        is_active=True,
    )
    create_user(user, session)
    return user


@pytest.fixture(name="test_token")
def test_token_fixture(test_user: User, secret_key: str) -> str:
    return create_access_token(
        {"id": test_user.id, "email": test_user.email, "role": test_user.roles.name},
        secret_key=secret_key,
    )
