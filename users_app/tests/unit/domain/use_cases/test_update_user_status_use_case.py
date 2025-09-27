from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.domain.models.user_callback_request import UserCallbackRequest
from src.domain.use_cases.update_user_status_use_case import UpdateUserStatusUseCase


def make_fake_user():
    user = MagicMock()
    user.id = "123"
    user.status = "VERIFICADO"
    user.email = "john@example.com"
    return user


def make_dto():
    return UserCallbackRequest(
        RUV="RUV123",
        userIdentifier="user-001",
        createdAt=datetime(2024, 1, 1, 12, 0, 0),
        status="VERIFICADO",
        score=85,
        verifyToken="token-xyz",
    )


def test_execute_calls_patch_and_email():
    fake_user = make_fake_user()
    patch_uc = MagicMock()
    patch_uc.execute.return_value = fake_user
    email_uc = MagicMock()

    uc = UpdateUserStatusUseCase(patch_uc, email_uc)
    dto = make_dto()

    result = uc.execute("123", dto)

    patch_uc.execute.assert_called_once_with("123", dto)
    email_uc.execute.assert_called_once_with(fake_user)
    assert result == fake_user


def test_execute_propagates_error_from_patch():
    patch_uc = MagicMock()
    patch_uc.execute.side_effect = ValueError("patch failed")
    email_uc = MagicMock()

    uc = UpdateUserStatusUseCase(patch_uc, email_uc)
    dto = make_dto()

    with pytest.raises(ValueError, match="patch failed"):
        uc.execute("123", dto)

    email_uc.execute.assert_not_called()


def test_execute_propagates_error_from_email():
    fake_user = make_fake_user()
    patch_uc = MagicMock()
    patch_uc.execute.return_value = fake_user
    email_uc = MagicMock()
    email_uc.execute.side_effect = RuntimeError("email failed")

    uc = UpdateUserStatusUseCase(patch_uc, email_uc)
    dto = make_dto()

    with pytest.raises(RuntimeError, match="email failed"):
        uc.execute("123", dto)

    patch_uc.execute.assert_called_once_with("123", dto)
    email_uc.execute.assert_called_once_with(fake_user)
