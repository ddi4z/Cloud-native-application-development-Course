from abc import ABC, abstractmethod
from src.domain.models.user_verify_request import UserVerifyRequest


class IdentityVerifierPort(ABC):
    """Identity verifier port interface."""

    @abstractmethod
    def verify(self, user_information: UserVerifyRequest) -> None:
        """Verify user identity."""
        raise NotImplementedError("This method should be overridden by subclasses.")
