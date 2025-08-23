from uuid import uuid4

import pytest

from src.domain.use_cases.delete_post_use_case import DeletePostUseCase


def test_delete_post_use_case_initializes_with_repository(mock_post_repository):
    use_case = DeletePostUseCase(post_repository=mock_post_repository)
    assert use_case.post_repository is mock_post_repository


def test_execute_calls_repository_delete_and_returns_confirmation(
    delete_post_use_case, mock_post_repository
):
    post_id = uuid4()
    expected_message = {"message": f"Post {post_id} deleted successfully."}
    mock_post_repository.delete.return_value = expected_message

    actual_message = delete_post_use_case.execute(post_id)

    mock_post_repository.delete.assert_called_once_with(post_id)
    assert actual_message == expected_message


def test_execute_propagates_exceptions_from_repository(
    delete_post_use_case, mock_post_repository
):
    post_id = uuid4()
    mock_post_repository.delete.side_effect = Exception("Database error")

    with pytest.raises(Exception, match="Database error"):
        delete_post_use_case.execute(post_id)

    mock_post_repository.delete.assert_called_once_with(post_id)
