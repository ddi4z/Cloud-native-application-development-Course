import time
import pytest
import hashlib
from uuid import UUID
from datetime import datetime, timedelta, timezone
from src.domain.models.posts import Post
from src.domain.models.post_creation_request import PostCreationRequest
from src.adapters.postgres.post_repository_adapter import PostgresPostRepositoryAdapter
from src.errors import (
    MissingPostInformationError,
    InvalidExpirationDate,
    PostNotFoundError,
    InvalidCredentialsError,
    MissingIdError
)

"""
@pytest.fixture
def repo(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    return PostgresPostRepositoryAdapter()
"""

def test_init_raises_error_if_no_db_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL not set"):
        PostgresPostRepositoryAdapter()


def test_create_post_success(repo):
    creation_request = PostCreationRequest(
        routeId="11111111-1111-1111-1111-111111111111",
        expireAt=((datetime.now(timezone.utc) + timedelta(hours=24))),
        userId="22222222-2222-2222-2222-222222222222"
    )
    post = repo.create(creation_request)

    assert isinstance(post, Post)
    assert post.routeId == UUID("11111111-1111-1111-1111-111111111111")
    assert post.userId == UUID("22222222-2222-2222-2222-222222222222")
    assert isinstance(post.id, UUID)
    assert post.expireAt > datetime.now(timezone.utc)


def test_create_post_with_missing_info(repo):
    creation_request = PostCreationRequest(
        routeId="11111111-1111-1111-1111-111111111111",
        expireAt=((datetime.now(timezone.utc) + timedelta(hours=24))),
    )
    with pytest.raises(MissingPostInformationError, match="Route Id, Expiration date, and User id are all required."):
        repo.create(creation_request)


def test_create_post_with_exp_date_not_future(repo):
    creation_request = PostCreationRequest(
        routeId="11111111-1111-1111-1111-111111111111",
        expireAt=datetime.now(timezone.utc),
        userId="22222222-2222-2222-2222-222222222222"
    )

    time.sleep(0.01)
    
    with pytest.raises(InvalidExpirationDate, match="Expiration date must be in the future."):
        repo.create(creation_request)


def test_filter_with_correct_information(repo):
    route_id = UUID("11111111-1111-1111-1111-111111111111")
    owner_id = UUID("22222222-2222-2222-2222-222222222222")

    creation_request = PostCreationRequest(
        routeId=route_id,
        expireAt=datetime.now(timezone.utc) + timedelta(hours=24),
        userId=owner_id
    )
    repo.create(creation_request)

    filtered_posts = repo.filter(route=route_id, owner=owner_id)

    assert isinstance(filtered_posts, list)
    assert all(isinstance(p, Post) for p in filtered_posts)
    assert all(p.routeId == route_id and p.userId == owner_id for p in filtered_posts)


def test_query(repo):
    route_id = "11111111-1111-1111-1111-111111111111"
    user_id = "22222222-2222-2222-2222-222222222222"
    expire_at = (datetime.now(timezone.utc) + timedelta(hours=24))

    creation_request = PostCreationRequest(
        routeId=route_id,
        expireAt=expire_at,
        userId=user_id
    )

    created_post = repo.create(creation_request)

    created_post_id = created_post.id

    result = repo.query(created_post_id)

    assert isinstance(result, Post)
    assert result.id == created_post_id
    assert result.routeId == UUID(route_id)
    assert result.expireAt == expire_at
    assert isinstance(result.createdAt, datetime)


def test_query_wrong_information(repo):
    wrong_query_id = 'sadasd'

    with pytest.raises(InvalidCredentialsError, match="Id is required and must be a UUID string."):
        repo.query(wrong_query_id)


def test_query_non_existent_post(repo):
    non_existent_id = UUID('00000000-0000-0000-0000-000000000000')
    with pytest.raises(PostNotFoundError, match="The provided id is not in the database"):
        repo.query(non_existent_id)


def test_count_posts(repo):
    repo.create(PostCreationRequest(
        routeId='11111111-1111-1111-1111-111111111111',
        expireAt=datetime.now(timezone.utc) + timedelta(hours=24),
        userId='22222222-2222-2222-2222-222222222222'
    ))

    repo.create(PostCreationRequest(
        routeId='33333333-3333-3333-3333-333333333333',
        expireAt=datetime.now(timezone.utc) + timedelta(hours=24),
        userId='11111111-1111-1111-1111-111111111111'
    ))

    assert repo.count() == 2


def test_reset_users(repo):
    repo.create(PostCreationRequest(
        routeId='11111111-1111-1111-1111-111111111111',
        expireAt=datetime.now(timezone.utc) + timedelta(hours=24),
        userId='22222222-2222-2222-2222-222222222222'
    ))

    assert repo.count() == 1

    repo.reset()

    assert repo.count() == 0


def test_delete(repo):
    creation_request = PostCreationRequest(
        routeId="11111111-1111-1111-1111-111111111111",
        expireAt=datetime.now(timezone.utc) + timedelta(hours=24),
        userId="22222222-2222-2222-2222-222222222222"
    )

    created_post = repo.create(creation_request)
    repo.delete(created_post.id)

    assert repo.count() == 0