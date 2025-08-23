import pytest

from src.domain.use_cases.reset_users_use_case import ResetUsersUseCase


def test_reset_users_use_case_initializes_with_repository(mock_user_repository):
    use_case = ResetUsersUseCase(user_repository=mock_user_repository)
    assert use_case.user_repository is mock_user_repository


def test_execute_calls_repository_reset_and_returns_confirmation_message(
    reset_users_use_case, mock_user_repository
):
    expected_message = {"message": "All users deleted successfully."}
    mock_user_repository.reset.return_value = expected_message
    actual_message = reset_users_use_case.execute()
    mock_user_repository.reset.assert_called_once()
    assert actual_message == expected_message


def test_execute_propagates_exceptions_from_repository(
    reset_users_use_case, mock_user_repository
):
    mock_user_repository.reset.side_effect = Exception("Database error")
    with pytest.raises(Exception, match="Database error"):
        reset_users_use_case.execute()
    mock_user_repository.reset.assert_called_once()
