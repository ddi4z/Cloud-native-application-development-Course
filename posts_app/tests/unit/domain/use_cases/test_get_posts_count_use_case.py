from src.domain.use_cases.count_post_use_case import CountPostUseCase


def test_get_posts_count_use_case_initializes_with_repository(mock_post_repository):
    use_case = CountPostUseCase(post_repository=mock_post_repository)
    assert use_case.post_repository is mock_post_repository


def test_execute_calls_repository_count_and_returns_correct_value(
    count_posts_use_case, mock_post_repository
):
    expected_count = 5
    mock_post_repository.count.return_value = expected_count
    actual_count = count_posts_use_case.execute()
    mock_post_repository.count.assert_called_once()
    assert actual_count == expected_count


def test_execute_handles_zero_posts_correctly(
    count_posts_use_case, mock_post_repository
):
    mock_post_repository.count.return_value = 0
    actual_count = count_posts_use_case.execute()
    mock_post_repository.count.assert_called_once()
    assert actual_count == 0
