import pytest
from src.domain.use_cases.authenticate_user_use_case import AuthenticateUserUseCase
from src.errors import InvalidCredentialsError

def test_authenticate_user_use_case_initializes_with_repository(mock_user_repository):
    use_case = AuthenticateUserUseCase(user_repository=mock_user_repository)
    assert use_case.user_repository is mock_user_repository

def test_execute_calls_repository_authenticate_and_returns_user(authenticate_user_use_case, mock_user_repository, authenticated_user):
    username = "testuser"
    password = "secure_password"
    mock_user_repository.authenticate.return_value = authenticated_user

    result_user = authenticate_user_use_case.execute(username, password)
    mock_user_repository.authenticate.assert_called_once_with(username, password)
    assert result_user is authenticated_user
    assert result_user.username == username

def test_execute_propagates_invalid_credentials_error(authenticate_user_use_case, mock_user_repository):
    username = "wrong_user"
    password = "wrong_password"
    mock_user_repository.authenticate.side_effect = InvalidCredentialsError("Invalid username or password.")

    with pytest.raises(InvalidCredentialsError, match="Invalid username or password."):
        authenticate_user_use_case.execute(username, password)
    mock_user_repository.authenticate.assert_called_once_with(username, password)