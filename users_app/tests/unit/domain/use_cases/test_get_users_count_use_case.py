from src.domain.use_cases.get_users_count_use_case import GetUsersCountUseCase

def test_get_users_count_use_case_initializes_with_repository(mock_user_repository):
    use_case = GetUsersCountUseCase(user_repository=mock_user_repository)
    assert use_case.user_repository is mock_user_repository

def test_execute_calls_repository_count_and_returns_correct_value(get_users_count_use_case, mock_user_repository):
    expected_count = 5
    mock_user_repository.count.return_value = expected_count
    actual_count = get_users_count_use_case.execute()
    mock_user_repository.count.assert_called_once()
    assert actual_count == expected_count

def test_execute_handles_zero_users_correctly(get_users_count_use_case, mock_user_repository):
    mock_user_repository.count.return_value = 0
    actual_count = get_users_count_use_case.execute()
    mock_user_repository.count.assert_called_once()
    assert actual_count == 0