import pytest

from src.domain.use_cases.reset_post_use_case import ResetPostUseCase


def test_reset_posts_use_case_initializes_with_repository(mock_post_repository):
    use_case = ResetPostUseCase(post_repository=mock_post_repository)
    assert use_case.post_repository is mock_post_repository


def test_execute_calls_repository_reset_and_returns_confirmation_message(
    reset_posts_use_case, mock_post_repository
):
    expected_message = {"message": "All posts deleted successfully."}
    mock_post_repository.reset.return_value = expected_message
    actual_message = reset_posts_use_case.execute()
    mock_post_repository.reset.assert_called_once()
    assert actual_message == expected_message


def test_execute_propagates_exceptions_from_repository(
    reset_posts_use_case, mock_post_repository
):
    mock_post_repository.reset.side_effect = Exception("Database error")
    with pytest.raises(Exception, match="Database error"):
        reset_posts_use_case.execute()
    mock_post_repository.reset.assert_called_once()
