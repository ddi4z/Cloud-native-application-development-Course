import pytest

from src.domain.use_cases.ping_check_post_use_case import PingCheckPostUseCase


def test_ping_check_post_use_case_initializes_with_repository(mock_post_repository):
    use_case = PingCheckPostUseCase(post_repository=mock_post_repository)
    assert use_case.post_repository is mock_post_repository


def test_execute_calls_repository_ping_and_returns_true(
    ping_check_post_use_case, mock_post_repository
):
    mock_post_repository.ping.return_value = True

    result = ping_check_post_use_case.execute(id="dummy-id")

    mock_post_repository.ping.assert_called_once()
    assert result is True


def test_execute_calls_repository_ping_and_returns_false(
    ping_check_post_use_case, mock_post_repository
):
    mock_post_repository.ping.return_value = False

    result = ping_check_post_use_case.execute(id="dummy-id")

    mock_post_repository.ping.assert_called_once()
    assert result is False


def test_execute_propagates_exceptions_from_repository(
    ping_check_post_use_case, mock_post_repository
):
    mock_post_repository.ping.side_effect = Exception("Repository not reachable")

    with pytest.raises(Exception, match="Repository not reachable"):
        ping_check_post_use_case.execute(id="dummy-id")

    mock_post_repository.ping.assert_called_once()
