import pytest

from src.domain.use_cases.update_user_use_case import UpdateUserUseCase
from src.errors import UserNotFoundError


def test_update_user_use_case_initializes_with_repository(mock_user_repository):
    use_case = UpdateUserUseCase(user_repository=mock_user_repository)
    assert use_case.user_repository is mock_user_repository


def test_execute_calls_repository_update_and_returns_updated_user(
    update_user_use_case, mock_user_repository, existing_user, update_data
):
    updated_user_mock = update_data
    mock_user_repository.update.return_value = updated_user_mock
    updated_user = update_user_use_case.execute(existing_user.id, update_data)
    mock_user_repository.update.assert_called_once_with(existing_user.id, update_data)
    assert updated_user is updated_user_mock
    assert updated_user.fullName == "Updated User Name"


def test_execute_propagates_user_not_found_error(
    update_user_use_case, mock_user_repository, update_data
):
    user_id = "999"
    mock_user_repository.update.side_effect = UserNotFoundError(
        f"User with id {user_id} not found."
    )
    with pytest.raises(UserNotFoundError, match=f"User with id {user_id} not found."):
        update_user_use_case.execute(user_id, update_data)
    mock_user_repository.update.assert_called_once_with(user_id, update_data)
