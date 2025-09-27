import datetime
import os
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.memory.user_repository_adapter import InMemoryUserRepositoryAdapter
from src.adapters.postgres.user_repository_adapter import PostgresUserRepositoryAdapter
from src.domain.models.user import User, UserStatus
from src.domain.models.user_creation_request import UserCreationRequest
from src.domain.models.user_db import Base, UserDB
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.domain.use_cases.authenticate_user_use_case import AuthenticateUserUseCase
from src.domain.use_cases.create_user_use_case import CreateUserUseCase
from src.domain.use_cases.get_current_user_use_case import GetCurrentUserUseCase
from src.domain.use_cases.get_users_count_use_case import GetUsersCountUseCase
from src.domain.use_cases.reset_users_use_case import ResetUsersUseCase
from src.domain.use_cases.update_user_use_case import UpdateUserUseCase

@pytest.fixture
def valid_user_data():
    return {
        "id": None,
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "hashed_password_123",
        "full_name": "John Doe",
        "is_active": True,
    }


@pytest.fixture
def user_with_id():
    return User(
        id=1,
        username="johndoe",
        email="johndoe@example.com",
        hashed_password="hashed_password_123",
        full_name="John Doe",
        is_active=True,
    )


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def repo(db_session, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    repo_adapter = PostgresUserRepositoryAdapter()
    repo_adapter._get_session = MagicMock(return_value=db_session)

    repo_adapter.engine = db_session.bind
    Base.metadata.create_all(repo_adapter.engine)

    return repo_adapter


@pytest.fixture
def memory_repo():
    memory_repo = InMemoryUserRepositoryAdapter()
    memory_repo.reset()
    return memory_repo


@pytest.fixture
def create_user_db(db_session):
    def _create(username, email, password, salt, token, expire_at=None):
        user = UserDB(
            username=username,
            email=email,
            password=password,
            salt=salt,
            token=token,
            status=UserStatus.VERIFIED,
            expireAt=expire_at
            or (
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=1)
            ),
            createdAt=datetime.datetime.now(datetime.timezone.utc),
            updatedAt=datetime.datetime.now(datetime.timezone.utc),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create


@pytest.fixture
def mock_user_repository():
    return MagicMock(spec=UserRepositoryPort)


@pytest.fixture
def update_user_use_case(mock_user_repository):
    return UpdateUserUseCase(user_repository=mock_user_repository)


@pytest.fixture
def existing_user():
    return User(
        id="123",
        username="existinguser",
        email="existing@example.com",
        password="hashed_password",
        salt="salt",
        token="token",
        status=UserStatus.NOT_VERIFIED,
        fullName="Existing User",
        phoneNumber="1234567890",
        dni="12345678A",
        expireAt="2025-01-01T00:00:00",
        createdAt="2024-01-01T00:00:00",
        updatedAt="2024-01-01T00:00:00",
    )


@pytest.fixture
def update_data():
    return User(
        id="123",
        username="existinguser",
        email="existing@example.com",
        password="hashed_password",
        salt="salt",
        token="token",
        status=UserStatus.VERIFIED,
        fullName="Updated User Name",
        phoneNumber="0987654321",
        dni="87654321B",
        expireAt="2025-01-01T00:00:00",
        createdAt="2024-01-01T00:00:00",
        updatedAt="2024-01-01T00:00:00",
    )


@pytest.fixture
def reset_users_use_case(mock_user_repository):
    return ResetUsersUseCase(user_repository=mock_user_repository)


@pytest.fixture
def get_users_count_use_case(mock_user_repository):
    return GetUsersCountUseCase(user_repository=mock_user_repository)


@pytest.fixture
def get_current_user_use_case(mock_user_repository):
    return GetCurrentUserUseCase(user_repository=mock_user_repository)


@pytest.fixture
def current_user():
    return User(
        id="123",
        username="currentuser",
        email="current@example.com",
        password="hashed_password",
        salt="salt",
        token="valid_token",
        status=UserStatus.VERIFIED,
        fullName="Current User",
        phoneNumber="1234567890",
        dni="12345678A",
        expireAt="2025-01-01T00:00:00",
        createdAt="2024-01-01T00:00:00",
        updatedAt="2024-01-01T00:00:00",
    )


@pytest.fixture
def create_user_use_case(mock_user_repository):
    return CreateUserUseCase(user_repository=mock_user_repository)


@pytest.fixture
def valid_user_creation_request():
    return UserCreationRequest(
        username="testuser",
        email="test@example.com",
        password="secure_password",
        phoneNumber="1234567890",
        dni="12345678A",
        fullName="Test User",
    )


@pytest.fixture
def authenticate_user_use_case(mock_user_repository):
    return AuthenticateUserUseCase(user_repository=mock_user_repository)


@pytest.fixture
def authenticated_user():
    return User(
        id="123",
        username="testuser",
        email="test@example.com",
        password="hashed_password",
        salt="salt",
        token="new_token",
        status=UserStatus.VERIFIED,
        fullName="Test User",
        phoneNumber="1234567890",
        dni="12345678A",
        expireAt="2025-01-01T00:00:00",
        createdAt="2024-01-01T00:00:00",
        updatedAt="2024-01-01T00:00:00",
    )
