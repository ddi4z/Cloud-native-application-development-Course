from abc import ABC, abstractmethod
from typing import Optional

from src.domain.models.user import User
from src.domain.models.user_callback_request import UserCallbackRequest
from src.domain.models.user_creation_request import UserCreationRequest


class UserRepositoryPort(ABC):
    """User repository interface."""

    @abstractmethod
    def create(self, userDto: UserCreationRequest) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def update(self, user_id: str, user: User) -> User:
        """Update an existing user by ID."""
        pass

    @abstractmethod
    def patch(self, user_id: str, user: UserCallbackRequest) -> User:
        """Patch an existing user by ID."""
        pass

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        pass

    @abstractmethod
    def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a token."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get total number of users."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Delete all users."""
        pass
