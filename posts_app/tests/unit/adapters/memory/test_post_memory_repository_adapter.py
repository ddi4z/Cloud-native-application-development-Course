from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from src.domain.models.post_creation_request import PostCreationRequest
from src.errors import (
    InvalidCredentialsError,
    InvalidExpirationDate,
    MissingIdError,
    MissingPostInformationError,
    PostNotFoundError,
)


def make_post_request(expire_delta: int = 3600) -> PostCreationRequest:
    return PostCreationRequest(
        routeId=uuid4(),
        userId=uuid4(),
        expireAt=datetime.now(timezone.utc) + timedelta(seconds=expire_delta),
    )


def test_create_missing_fields(repo):
    request = make_post_request()
    request.routeId = None
    with pytest.raises(MissingPostInformationError):
        repo.create(request)


def test_create_invalid_expiration(repo):
    request = make_post_request(expire_delta=-60)
    with pytest.raises(InvalidExpirationDate):
        repo.create(request)


def test_filter_by_owner_and_route(repo):
    request = make_post_request()
    post = repo.create(request)

    by_owner = repo.filter(owner=post.userId)
    by_route = repo.filter(route=post.routeId)

    assert post.id in [p.id for p in by_owner]
    assert post.id in [p.id for p in by_route]


def test_filter_invalid_inputs(repo):
    with pytest.raises(InvalidCredentialsError):
        repo.filter(expire="yes")

    with pytest.raises(InvalidCredentialsError):
        repo.filter(route="not-uuid")

    with pytest.raises(InvalidCredentialsError):
        repo.filter(owner="not-uuid")


# ------------------------
# query
# ------------------------
def test_query_success(repo):
    request = make_post_request()
    post = repo.create(request)

    found = repo.query(str(post.id))
    assert found.id == post.id


def test_query_invalid_format(repo):
    with pytest.raises(InvalidCredentialsError):
        repo.query("")

    with pytest.raises(InvalidCredentialsError):
        repo.query("not-uuid")


def test_query_not_found(repo):
    with pytest.raises(PostNotFoundError):
        repo.query(str(uuid4()))


# ------------------------
# delete
# ------------------------
def test_delete_success(repo):
    request = make_post_request()
    post = repo.create(request)

    deleted = repo.delete(post.id)
    assert deleted.id == post.id
    assert repo.count() == 0


def test_delete_missing_id(repo):
    with pytest.raises(MissingIdError):
        repo.delete("")


def test_delete_invalid_format(repo):
    with pytest.raises(InvalidCredentialsError):
        repo.delete("not-uuid")


def test_delete_not_found(repo):
    with pytest.raises(PostNotFoundError):
        repo.delete(uuid4())


# ------------------------
# misc
# ------------------------
def test_count_and_ping_and_reset(repo):
    request = make_post_request()
    repo.create(request)

    assert repo.count() == 1
    assert repo.ping() == "pong"

    repo.reset()
    assert repo.count() == 0
