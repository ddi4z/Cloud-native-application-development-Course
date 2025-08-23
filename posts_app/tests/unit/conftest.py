from datetime import datetime, timezone, timedelta
from uuid import UUID
from unittest.mock import MagicMock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models.posts import Post
from src.domain.models.post_db import PostDB, Base
from src.domain.models.post_creation_request import PostCreationRequest

from src.adapters.postgres.post_repository_adapter import PostgresPostRepositoryAdapter

from src.domain.ports.post_repository_port import PostRepositoryPort

from src.domain.use_cases.count_post_use_case import CountPostUseCase
from src.domain.use_cases.create_post_use_case import CreatePostUseCase
from src.domain.use_cases.delete_post_use_case import DeletePostUseCase
from src.domain.use_cases.filter_post_use_case import FilterPostUseCase
from src.domain.use_cases.query_post_use_case import QueryPostUseCase
from src.domain.use_cases.reset_post_use_case import ResetPostUseCase


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
    
    repo_adapter = PostgresPostRepositoryAdapter()
    repo_adapter._get_session = MagicMock(return_value=db_session)
    
    repo_adapter.engine = db_session.bind
    Base.metadata.create_all(repo_adapter.engine)
    
    return repo_adapter

@pytest.fixture
def mock_post_repository():
    return MagicMock(spec=PostRepositoryPort)

@pytest.fixture
def count_post_use_case(mock_post_repository):
    return CountPostUseCase(post_repository=mock_post_repository)


@pytest.fixture
def create_post_db(db_session):
    def _create(id, routeId, userId, expireAt=None, createdAt=None):
        post = PostDB(
            id=id,
            routeId=routeId,
            userId=userId,
            expireAt=expireAt or (datetime.now(timezone.utc) + timedelta(hours=1)),
            createdAt=createdAt or datetime.now(timezone.utc)
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        return post
    return _create

@pytest.fixture
def create_post_use_case(mock_user_repository):
    return CreatePostUseCase(post_repository=mock_user_repository)

@pytest.fixture
def delete_post_use_case(mock_user_repository):
    return DeletePostUseCase(post_repository=mock_user_repository)

@pytest.fixture
def delete_post_db(db_session):
    def _delete(post_id):
        post = db_session.query(PostDB).get(post_id)
        if post:
            db_session.delete(post)
            db_session.commit()
        return post
    return _delete

@pytest.fixture
def filter_post_use_case(mock_user_repository):
    return FilterPostUseCase(post_repository=mock_user_repository)


@pytest.fixture
def existing_post():
    return Post(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        routeId=UUID("22222222-2222-2222-2222-222222222222"),
        userId=UUID("33333333-3333-3333-3333-333333333333"),
        expireAt=datetime.now(timezone.utc) + timedelta(hours=24),
        createdAt=datetime.now(timezone.utc)
    )

@pytest.fixture
def reset_post_use_case(mock_user_repository):
    return ResetPostUseCase(post_repository=mock_user_repository)

@pytest.fixture
def query_post_use_case(mock_user_repository):
    return QueryPostUseCase(post_repository=mock_user_repository)

@pytest.fixture
def valid_post_creation_request():
    return PostCreationRequest(
        routeId=UUID("22222222-2222-2222-2222-222222222222"),
        expireAt=datetime.now(timezone.utc) + timedelta(hours=24),
        userId=UUID("33333333-3333-3333-3333-333333333333"),
    )

@pytest.fixture
def valid_post_data():
    return {
        "id": UUID("11111111-1111-1111-1111-111111111111"),
        "routeId": UUID("22222222-2222-2222-2222-222222222222"),
        "userId": UUID("33333333-3333-3333-3333-333333333333"),
        "expireAt": datetime.now(timezone.utc) + timedelta(hours=24),
        "createdAt": datetime.now(timezone.utc)
    }