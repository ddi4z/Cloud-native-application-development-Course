from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.domain.models.posts import Post
from src.domain.use_cases.create_post_use_case import CreatePostUseCase


def make_fake_post():
    """Crea un post de prueba para el mock."""
    return Post(
        id=uuid4(),
        routeId=uuid4(),
        userId=uuid4(),
        expireAt=datetime.now(timezone.utc),
        createdAt=datetime.now(timezone.utc),
    )


def test_create_post_use_case_initializes_with_repository(mock_post_repository):
    use_case = CreatePostUseCase(post_repository=mock_post_repository)
    assert use_case.post_repository is mock_post_repository


def test_execute_calls_repository_create_and_returns_post(
    create_post_use_case, mock_post_repository
):
    fake_post = make_fake_post()
    mock_post_repository.create.return_value = fake_post

    result = create_post_use_case.execute(fake_post)

    mock_post_repository.create.assert_called_once_with(fake_post)
    assert result == fake_post


def test_execute_returns_none_if_repository_returns_none(
    create_post_use_case, mock_post_repository
):
    fake_post = make_fake_post()
    mock_post_repository.create.return_value = None

    result = create_post_use_case.execute(fake_post)

    mock_post_repository.create.assert_called_once_with(fake_post)
    assert result is None


def test_execute_propagates_exceptions_from_repository(
    create_post_use_case, mock_post_repository
):
    fake_post = make_fake_post()
    mock_post_repository.create.side_effect = Exception("Database error")

    with pytest.raises(Exception, match="Database error"):
        create_post_use_case.execute(fake_post)

    mock_post_repository.create.assert_called_once_with(fake_post)
