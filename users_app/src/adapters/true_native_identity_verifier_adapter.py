from asyncio.log import logger
import os
import sys
import requests
from requests.models import Response

from src.domain.models.user_verify_request import UserVerifyRequest
from src.domain.ports.identity_verifier_port import IdentityVerifierPort

from .catch_unavailable_service import catch_unavailable_service


class TrueNativeIdentityVerifierAdapter(IdentityVerifierPort):
    """TrueNative Identity Verifier Adapter."""

    def __init__(self, service_url: str):
        self.service_url = service_url
        self.secret_token = os.getenv("SECRET_TOKEN", "token")

    #@catch_unavailable_service("TrueNative Identity Verifier")
    def verify(self, user_information: UserVerifyRequest) -> None:
        print(f">>> Entrando a verify con {user_information}", flush=True, file=sys.stdout)
        print(f">>> Haciendo request a {self.service_url}", flush=True, file=sys.stdout)

        response: Response = requests.post(
            self.service_url,
            json=user_information.model_dump(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.secret_token}"
            },
            timeout=10,
        )

        print(f">>> Response status code: {response.status_code}", flush=True, file=sys.stdout)
        print(f">>> Response body: {response.text}", flush=True, file=sys.stdout)

        if response.status_code != 201:
            return None

        return response.json()