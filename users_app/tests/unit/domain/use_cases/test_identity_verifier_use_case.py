from unittest.mock import MagicMock

import pytest

from src.domain.models.user_verify_request import UserData, UserVerifyRequest
from src.domain.use_cases.identity_verifier_use_case import IdentityVerifierUseCase


def make_fake_request() -> UserVerifyRequest:
    return UserVerifyRequest(
        user=UserData(
            email="john@example.com",
            dni="123456789",
            fullName="John Doe",
            phone="1234567890",
        ),
        transactionIdentifier="tx-999",
        userIdentifier="user-999",
        userWebhook="http://fake-webhook.com",
    )


def test_execute_calls_identity_verifier_with_request():
    fake_request = make_fake_request()
    verifier = MagicMock()
    uc = IdentityVerifierUseCase(verifier)

    uc.execute(fake_request)

    verifier.verify.assert_called_once_with(fake_request)


def test_execute_returns_result_from_verifier():
    fake_request = make_fake_request()
    verifier = MagicMock()
    verifier.verify.return_value = {"status": "ok"}
    uc = IdentityVerifierUseCase(verifier)

    result = uc.execute(fake_request)

    assert result == {"status": "ok"}


def test_execute_propagates_exception_from_verifier():
    fake_request = make_fake_request()
    verifier = MagicMock()
    verifier.verify.side_effect = RuntimeError("service unavailable")
    uc = IdentityVerifierUseCase(verifier)

    with pytest.raises(RuntimeError, match="service unavailable"):
        uc.execute(fake_request)
