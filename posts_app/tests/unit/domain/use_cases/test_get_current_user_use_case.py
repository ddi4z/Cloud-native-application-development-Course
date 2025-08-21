import pytest
from src.domain.use_cases.get_current_user_use_case import GetCurrentUserUseCase
from src.errors import InvalidTokenError, MissingTokenError

def test_get_current_user_use_case_initializes_with_repository(mock_user_repository):
    use_case = GetCurrentUserUseCase(user_repository=mock_user_repository)
    assert use_case.user_repository is mock_user_repository

def test_execute_calls_repository_get_current_user_and_returns_user(get_current_user_use_case, mock_user_repository, current_user):
    valid_token = "valid_token_123"
    mock_user_repository.get_current_user.return_value = current_user
    result_user = get_current_user_use_case.execute(valid_token)
    mock_user_repository.get_current_user.assert_called_once_with(valid_token)
    assert result_user is current_user
    assert result_user.username == "currentuser"

def test_execute_propagates_missing_token_error(get_current_user_use_case, mock_user_repository):
    mock_user_repository.get_current_user.side_effect = MissingTokenError("Token is missing.")
    with pytest.raises(MissingTokenError, match="Token is missing."):
        get_current_user_use_case.execute(None)
    mock_user_repository.get_current_user.assert_called_once_with(None)

def test_execute_propagates_invalid_token_error(get_current_user_use_case, mock_user_repository):
    invalid_token = "invalid_token_123"
    mock_user_repository.get_current_user.side_effect = InvalidTokenError("The token is invalid or has expired.")
    with pytest.raises(InvalidTokenError, match="The token is invalid or has expired."):
        get_current_user_use_case.execute(invalid_token)
    mock_user_repository.get_current_user.assert_called_once_with(invalid_token)