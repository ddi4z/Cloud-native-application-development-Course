from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.memory.post_repository_adapter import InMemoryPostRepositoryAdapter
from src.adapters.postgres.post_repository_adapter import PostgresPostRepositoryAdapter
from src.domain.models.post_creation_request import PostCreationRequest
from src.domain.models.post_db import Base, PostDB
from src.domain.models.posts import Post
from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.count_post_use_case import CountPostUseCase
from src.domain.use_cases.create_post_use_case import CreatePostUseCase
from src.domain.use_cases.delete_post_use_case import DeletePostUseCase
from src.domain.use_cases.filter_post_use_case import FilterPostUseCase
from src.domain.use_cases.ping_check_post_use_case import PingCheckPostUseCase
from src.domain.use_cases.reset_post_use_case import ResetPostUseCase
from tests.unit.domain.use_cases.test_query_post_use_case import QueryPostUseCase


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
def repo():
    repo = InMemoryPostRepositoryAdapter()
    repo.reset()
    return repo


@pytest.fixture(scope="function", autouse=True)
def setup_test_db(monkeypatch):
    test_db_url = "sqlite+pysqlite:///:memory:"
    monkeypatch.setenv("DATABASE_URL", test_db_url)

    adapter = PostgresPostRepositoryAdapter()
    adapter.reset()
    yield adapter
    adapter.reset()


@pytest.fixture
def mock_post_repository():
    return MagicMock(spec=PostRepositoryPort)


@pytest.fixture
def count_posts_use_case(mock_post_repository):
    return CountPostUseCase(post_repository=mock_post_repository)


@pytest.fixture
def reset_posts_use_case(mock_post_repository):
    return ResetPostUseCase(post_repository=mock_post_repository)


@pytest.fixture
def delete_post_use_case(mock_post_repository):
    return DeletePostUseCase(post_repository=mock_post_repository)


@pytest.fixture
def filter_post_use_case(mock_post_repository):
    return FilterPostUseCase(post_repository=mock_post_repository)


@pytest.fixture
def ping_check_post_use_case(mock_post_repository):
    return PingCheckPostUseCase(post_repository=mock_post_repository)


@pytest.fixture
def query_post_use_case(mock_post_repository):
    return QueryPostUseCase(post_repository=mock_post_repository)


@pytest.fixture
def create_post_use_case(mock_post_repository):
    return CreatePostUseCase(post_repository=mock_post_repository)


@pytest.fixture
def valid_post_request():
    return PostCreationRequest(
        routeId=uuid4(),
        userId=uuid4(),
        expireAt=datetime.now(timezone.utc) + timedelta(hours=1),
    )
