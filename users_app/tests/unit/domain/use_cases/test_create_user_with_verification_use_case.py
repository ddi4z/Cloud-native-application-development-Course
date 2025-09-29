from unittest.mock import MagicMock
import pytest

from src.domain.models.user_creation_request import UserCreationRequest
from src.domain.models.user_verify_request import UserVerifyRequest
from src.domain.use_cases.create_user_with_verification_use_case import (
    CreateUserWithVerificationUseCase,
)


def make_fake_user():
    user = MagicMock()
    user.id = "123"
    user.fullName = "John Doe"
    user.dni = "123456789"
    user.email = "john@example.com"
    user.phone = "+573001112233" 
    return user

def test_execute_calls_create_and_verify():
    fake_user = make_fake_user()
    create_uc = MagicMock()
    create_uc.execute.return_value = fake_user
    verify_uc = MagicMock()

    uc = CreateUserWithVerificationUseCase(create_uc, verify_uc)
    dto = UserCreationRequest(username="john", email="john@example.com", password="pwd")

    result = uc.execute(dto)

    create_uc.execute.assert_called_once_with(dto)
    verify_uc.execute.assert_called_once()
    args, _ = verify_uc.execute.call_args
    verify_request = args[0]
    assert isinstance(verify_request, UserVerifyRequest)

    assert verify_request.user.fullName == fake_user.fullName
    assert verify_request.user.dni == fake_user.dni
    assert verify_request.user.email == fake_user.email

    assert isinstance(verify_request.transactionIdentifier, str)
    assert isinstance(verify_request.userIdentifier, str)
    assert isinstance(verify_request.userWebhook, str)
    assert result == fake_user


def test_execute_propagates_error_from_create():
    create_uc = MagicMock()
    create_uc.execute.side_effect = ValueError("boom")
    verify_uc = MagicMock()

    uc = CreateUserWithVerificationUseCase(create_uc, verify_uc)
    dto = UserCreationRequest(username="john", email="john@example.com", password="pwd")

    with pytest.raises(ValueError, match="boom"):
        uc.execute(dto)

    verify_uc.execute.assert_not_called()


def test_execute_propagates_error_from_verify():
    fake_user = make_fake_user()
    create_uc = MagicMock()
    create_uc.execute.return_value = fake_user
    verify_uc = MagicMock()
    verify_uc.execute.side_effect = RuntimeError("verify failed")

    uc = CreateUserWithVerificationUseCase(create_uc, verify_uc)
    dto = UserCreationRequest(username="john", email="john@example.com", password="pwd")

    with pytest.raises(RuntimeError, match="verify failed"):
        uc.execute(dto)

    create_uc.execute.assert_called_once()
    verify_uc.execute.assert_called_once()
