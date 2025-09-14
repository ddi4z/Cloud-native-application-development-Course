from abc import abstractmethod
from typing import Optional
from src.domain.models.user import User

from .http_request import HttpRequest


class UserValidationPort(HttpRequest):
    """Offer repository interface."""

    @abstractmethod
    def validate_token_and_get_user(self, token: str) -> Optional[User]:
        """Validate the auth token and get the user."""
        raise NotImplementedError("This method should be overridden in subclasses")
