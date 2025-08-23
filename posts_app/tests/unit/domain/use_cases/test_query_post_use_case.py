from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.domain.models.posts import Post
from src.domain.use_cases.query_post_use_case import QueryPostUseCase


def make_fake_post():
    return Post(
        id=uuid4(),
        routeId=uuid4(),
        userId=uuid4(),
        expireAt=datetime.now(timezone.utc),
        createdAt=datetime.now(timezone.utc),
    )


def test_query_post_use_case_initializes_with_repository(mock_post_repository):
    use_case = QueryPostUseCase(post_repository=mock_post_repository)
    assert use_case.post_repository is mock_post_repository


def test_execute_calls_repository_query_and_returns_post(
    query_post_use_case, mock_post_repository
):
    fake_post = make_fake_post()
    mock_post_repository.query.return_value = fake_post

    result = query_post_use_case.execute(id=fake_post.id)

    mock_post_repository.query.assert_called_once_with(fake_post.id)
    assert result == fake_post


def test_execute_returns_none_if_post_not_found(
    query_post_use_case, mock_post_repository
):
    mock_post_repository.query.return_value = None
    result = query_post_use_case.execute(id=uuid4())

    mock_post_repository.query.assert_called_once()
    assert result is None


def test_execute_propagates_exceptions_from_repository(
    query_post_use_case, mock_post_repository
):
    mock_post_repository.query.side_effect = Exception("Database error")

    with pytest.raises(Exception, match="Database error"):
        query_post_use_case.execute(id=uuid4())

    mock_post_repository.query.assert_called_once()
