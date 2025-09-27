import requests
from requests.models import Response

from src.domain.models.user_verify_request import UserVerifyRequest
from src.domain.ports.identity_verifier_port import IdentityVerifierPort

from .catch_unavailable_service import catch_unavailable_service


class TrueNativeIdentityVerifierAdapter(IdentityVerifierPort):
    """TrueNative Identity Verifier Adapter."""

    def __init__(self, service_url: str):
        self.service_url = service_url

    @catch_unavailable_service("TrueNative Identity Verifier")
    def verify(self, user_information: UserVerifyRequest) -> None:
        response: Response = requests.post(
            self.service_url,
            json=user_information.model_dump(),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 201:
            return None

        return response.json()
