from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock
from src.domain.use_cases.send_user_email_use_case import SendUserEmailUseCase
from src.domain.models.user import User, UserStatus


def make_fake_user() -> User:
    now = datetime.now()
    return User(
        id="123",
        username="johndoe",
        email="john@example.com",
        phoneNumber="1234567890",
        dni="123456789",
        fullName="John Doe",
        password="hashedpwd",
        salt="randomsalt",
        token="token123",
        status=UserStatus.VERIFIED,
        expireAt=now + timedelta(days=1),
        createdAt=now,
        updatedAt=now,
    )


def test_execute_calls_send_message_with_user():
    user = make_fake_user()
    mq_port = MagicMock()
    uc = SendUserEmailUseCase(mq_port)

    uc.execute(user)

    mq_port.send_message.assert_called_once_with(user)


def test_execute_returns_result_from_message_queue():
    user = make_fake_user()
    mq_port = MagicMock()
    mq_port.send_message.return_value = "queued"
    uc = SendUserEmailUseCase(mq_port)

    result = uc.execute(user)

    assert result == "queued"


def test_execute_propagates_exception_from_message_queue():
    user = make_fake_user()
    mq_port = MagicMock()
    mq_port.send_message.side_effect = RuntimeError("queue unavailable")
    uc = SendUserEmailUseCase(mq_port)

    with pytest.raises(RuntimeError, match="queue unavailable"):
        uc.execute(user)
