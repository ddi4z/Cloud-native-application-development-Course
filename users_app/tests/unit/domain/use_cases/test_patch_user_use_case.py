import pytest
from unittest.mock import MagicMock
from datetime import datetime
from src.domain.use_cases.patch_user_use_case import PatchUserUseCase
from src.domain.models.user import User, UserStatus
from src.domain.models.user_callback_request import UserCallbackRequest


def make_fake_user() -> User:
    """Crea un User válido para pruebas."""
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
        expireAt=now,
        createdAt=now,
        updatedAt=now,
    )


def make_fake_callback() -> UserCallbackRequest:
    """Crea un UserCallbackRequest válido para pruebas."""
    return UserCallbackRequest(
        RUV="RUV123",
        score=95,
        userIdentifier="uid123",
        createdAt=datetime.now(),
        status="VERIFICADO",
        verifyToken="sometoken",
    )


def test_execute_calls_patch_with_correct_arguments():
    repo = MagicMock()
    uc = PatchUserUseCase(repo)
    callback = make_fake_callback()

    uc.execute("123", callback)

    repo.patch.assert_called_once_with("123", callback)


def test_execute_returns_user_from_repository():
    repo = MagicMock()
    fake_user = make_fake_user()
    repo.patch.return_value = fake_user
    uc = PatchUserUseCase(repo)
    callback = make_fake_callback()

    result = uc.execute("123", callback)

    assert result == fake_user


def test_execute_propagates_exception_from_repository():
    repo = MagicMock()
    repo.patch.side_effect = RuntimeError("DB error")
    uc = PatchUserUseCase(repo)
    callback = make_fake_callback()

    with pytest.raises(RuntimeError, match="DB error"):
        uc.execute("123", callback)
