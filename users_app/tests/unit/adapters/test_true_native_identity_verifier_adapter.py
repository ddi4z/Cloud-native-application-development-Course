import pytest
from unittest.mock import patch, MagicMock

from src.adapters.true_native_identity_verifier_adapter import (
    TrueNativeIdentityVerifierAdapter,
)
from src.domain.models.user_verify_request import UserVerifyRequest


@pytest.fixture
def adapter():
    return TrueNativeIdentityVerifierAdapter(service_url="http://fake-service.com")


@pytest.fixture
def user_request():
    return UserVerifyRequest(
        email="test@example.com",
        dni="123456789",
        fullName="John Doe",
        phone="+573001112233",
    )


def test_verify_success(adapter, user_request):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"status": "VERIFIED"}

    with patch(
        "src.adapters.true_native_identity_verifier_adapter.requests.post",
        return_value=mock_response,
    ) as mock_post:
        result = adapter.verify(user_request)

    mock_post.assert_called_once_with(
        "http://fake-service.com",
        json=user_request.model_dump(),
        headers={"Content-Type": "application/json"},
    )
    assert result == {"status": "VERIFIED"}


def test_verify_failure_non_201(adapter, user_request):
    mock_response = MagicMock()
    mock_response.status_code = 400

    with patch(
        "src.adapters.true_native_identity_verifier_adapter.requests.post",
        return_value=mock_response,
    ):
        result = adapter.verify(user_request)

    assert result is None


def test_verify_service_unavailable(adapter, user_request):
    with patch(
        "src.adapters.true_native_identity_verifier_adapter.requests.post",
        side_effect=Exception("Service down"),
    ):
        with pytest.raises(Exception) as exc_info:
            adapter.verify(user_request)

    assert "Service down" in str(exc_info.value)
