from typing import Dict, Optional

from users_app.src.domain.models.user import User
from users_app.src.domain.ports.user_repository_port import UserRepositoryPort
from errors import UserNotFoundError, AuthenticationError


class InMemoryUserRepositoryAdapter(UserRepositoryPort):
    """In-memory implementation of UserRepository."""

    memory_store: Dict[int, User] = {}
    tokens_store: Dict[str, int] = {}

    def sequence(self) -> int:
        """Generate a new sequence number."""
        return len(self.memory_store) + 1

    def create(self, user: User) -> User:
        """Create a new user."""
        user.id = self.sequence()
        self.memory_store[user.id] = user
        return user

    def update(self, user_id: str, user: User) -> User:
        """Update an existing user by ID."""
        if user_id not in self.memory_store:
            raise UserNotFoundError(f"User with id {user_id} not found")
        self.memory_store[user_id] = user
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        for user in self.memory_store.values():
            if user.username == username and user.password == password:
                token = f"token-{user.id}"
                self.tokens_store[token] = user.id
                return user
        raise AuthenticationError("Invalid username or password")

    def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a token."""
        user_id = self.tokens_store.get(token)
        if not user_id:
            return None
        return self.memory_store.get(user_id)

    def count(self) -> int:
        """Get total number of users."""
        return len(self.memory_store)

    def reset(self) -> dict:
        """Delete all users and return confirmation message."""
        self.memory_store.clear()
        self.tokens_store.clear()
        return {"msg": "Todos los datos fueron eliminados"}
