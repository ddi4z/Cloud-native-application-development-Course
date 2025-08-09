from abc import ABC, abstractmethod
from typing import List, Optional

from users_app.src.domain.models.user import User


class UserRepositoryPort(ABC):
    """User repository interface."""

    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def update(self, user_id: str, user: User) -> User:
        """Update an existing user by ID."""
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
    def reset(self) -> dict:
        """Delete all users and return confirmation message."""
        pass
