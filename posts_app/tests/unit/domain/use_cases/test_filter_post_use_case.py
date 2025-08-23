from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.domain.models.posts import Post
from src.domain.use_cases.filter_post_use_case import FilterPostUseCase


def test_filter_post_use_case_initializes_with_repository(mock_post_repository):
    use_case = FilterPostUseCase(post_repository=mock_post_repository)
    assert use_case.post_repository is mock_post_repository


def test_execute_calls_repository_filter_and_returns_results(
    filter_post_use_case, mock_post_repository
):
    fake_post = Post(
        id=uuid4(),
        routeId=uuid4(),
        userId=uuid4(),
        expireAt=datetime.now(timezone.utc),
        createdAt=datetime.now(timezone.utc),
    )
    expected_posts = [fake_post]
    mock_post_repository.filter.return_value = expected_posts

    result = filter_post_use_case.execute(
        expire=False, route=fake_post.routeId, owner=fake_post.userId
    )

    mock_post_repository.filter.assert_called_once_with(
        False, fake_post.routeId, fake_post.userId
    )
    assert result == expected_posts


def test_execute_with_no_filters_returns_all_posts(
    filter_post_use_case, mock_post_repository
):
    expected_posts = []
    mock_post_repository.filter.return_value = expected_posts

    result = filter_post_use_case.execute()

    mock_post_repository.filter.assert_called_once_with(None, None, None)
    assert result == expected_posts


def test_execute_propagates_exceptions_from_repository(
    filter_post_use_case, mock_post_repository
):
    mock_post_repository.filter.side_effect = Exception("Database error")

    with pytest.raises(Exception, match="Database error"):
        filter_post_use_case.execute()

    mock_post_repository.filter.assert_called_once_with(None, None, None)
