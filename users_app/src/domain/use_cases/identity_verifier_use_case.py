from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.models.user_verify_request import UserVerifyRequest
from src.domain.ports.identity_verifier_port import IdentityVerifierPort


class IdentityVerifierUseCase(BaseUseCase):
    """Use case for verifying user identity."""

    def __init__(self, identity_verifier: IdentityVerifierPort):
        self.identity_verifier = identity_verifier

    def execute(self, user: UserVerifyRequest) -> None:
        """Verify user identity."""
        return self.identity_verifier.verify(user)
