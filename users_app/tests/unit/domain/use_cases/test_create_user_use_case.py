from unittest.mock import MagicMock

import pytest

from src.domain.models.user import User
from src.domain.use_cases.create_user_use_case import CreateUserUseCase
from src.errors import UserAlreadyExistsError


def test_create_user_use_case_initializes_with_repository(mock_user_repository):
    use_case = CreateUserUseCase(user_repository=mock_user_repository)
    assert use_case.user_repository is mock_user_repository


def test_execute_calls_repository_create_and_returns_user(
    create_user_use_case, mock_user_repository, valid_user_creation_request
):
    mock_created_user = MagicMock(spec=User)
    mock_created_user.username = valid_user_creation_request.username
    mock_created_user.email = valid_user_creation_request.email
    mock_user_repository.create.return_value = mock_created_user
    created_user = create_user_use_case.execute(valid_user_creation_request)
    mock_user_repository.create.assert_called_once_with(valid_user_creation_request)
    assert created_user is mock_created_user


def test_execute_propagates_repository_errors(
    create_user_use_case, mock_user_repository, valid_user_creation_request
):
    mock_user_repository.create.side_effect = UserAlreadyExistsError(
        "User already exists"
    )
    with pytest.raises(UserAlreadyExistsError, match="User already exists"):
        create_user_use_case.execute(valid_user_creation_request)
    mock_user_repository.create.assert_called_once_with(valid_user_creation_request)
