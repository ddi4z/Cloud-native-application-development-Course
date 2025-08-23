from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.adapters.postgres.post_repository_adapter import PostgresPostRepositoryAdapter
from src.domain.models.post_creation_request import PostCreationRequest
from src.domain.models.post_db import Base, PostDB
from src.domain.models.posts import Post
from src.errors import (
    InvalidCredentialsError,
    InvalidExpirationDate,
    MissingIdError,
    MissingPostInformationError,
    PostNotFoundError,
)


def test_create_post_success(setup_test_db, valid_post_request):
    repo = setup_test_db
    post = repo.create(valid_post_request)
    assert post.id is not None
    assert post.routeId == valid_post_request.routeId
    assert post.userId == valid_post_request.userId
    assert post.expireAt.replace(tzinfo=timezone.utc) == valid_post_request.expireAt
    assert repo.count() == 1


def test_create_post_missing_fields(setup_test_db, valid_post_request):
    repo = setup_test_db
    req = valid_post_request
    req.routeId = None

    with pytest.raises(MissingPostInformationError):
        repo.create(req)


def test_create_post_expired_date(setup_test_db):
    repo = setup_test_db
    req = PostCreationRequest(
        routeId=uuid4(),
        userId=uuid4(),
        expireAt=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    with pytest.raises(InvalidExpirationDate):
        repo.create(req)


def test_filter_by_expired_and_owner(setup_test_db, valid_post_request):
    repo = setup_test_db
    repo.create(valid_post_request)

    expired_post = PostDB(
        id=uuid4(),
        routeId=uuid4(),
        userId=valid_post_request.userId,
        expireAt=datetime.now(timezone.utc) - timedelta(minutes=1),
        createdAt=datetime.now(timezone.utc),
    )
    with repo._get_session() as db:
        db.add(expired_post)
        db.commit()

    not_expired = repo.filter(expire=False)
    expired = repo.filter(expire=True)

    now = datetime.now(timezone.utc)

    def _ensure_utc(dt):
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    assert all(_ensure_utc(p.expireAt) > now for p in not_expired)
    assert all(_ensure_utc(p.expireAt) <= now for p in expired)


def test_filter_by_route_and_owner(setup_test_db, valid_post_request):
    repo = setup_test_db
    post = repo.create(valid_post_request)

    result_by_route = repo.filter(route=post.routeId)
    result_by_owner = repo.filter(owner=post.userId)

    assert len(result_by_route) == 1
    assert result_by_route[0].id == post.id

    assert len(result_by_owner) == 1
    assert result_by_owner[0].id == post.id


def test_query_existing_post(setup_test_db, valid_post_request):
    repo = setup_test_db
    post = repo.create(valid_post_request)

    queried = repo.query(str(post.id))
    assert queried.id == post.id


def test_query_invalid_uuid(setup_test_db):
    repo = setup_test_db
    with pytest.raises(InvalidCredentialsError):
        repo.query("not-a-uuid")


def test_query_non_existing_post(setup_test_db):
    repo = setup_test_db
    with pytest.raises(PostNotFoundError):
        repo.query(str(uuid4()))


def test_delete_post_success(setup_test_db, valid_post_request):
    repo = setup_test_db
    post = repo.create(valid_post_request)

    deleted = repo.delete(post.id)
    assert deleted.id == post.id
    assert repo.count() == 0


def test_delete_post_invalid_uuid(setup_test_db):
    repo = setup_test_db
    with pytest.raises(InvalidCredentialsError):
        repo.delete("invalid-uuid")


def test_delete_non_existing_post(setup_test_db):
    repo = setup_test_db
    with pytest.raises(PostNotFoundError):
        repo.delete(uuid4())


def test_delete_missing_id(setup_test_db):
    repo = setup_test_db
    with pytest.raises(MissingIdError):
        repo.delete("")


def test_ping_returns_pong(setup_test_db):
    repo = setup_test_db
    assert repo.ping() == "pong"


def test_count_and_reset(setup_test_db, valid_post_request):
    repo = setup_test_db
    repo.create(valid_post_request)
    assert repo.count() == 1
    repo.reset()
    assert repo.count() == 0
