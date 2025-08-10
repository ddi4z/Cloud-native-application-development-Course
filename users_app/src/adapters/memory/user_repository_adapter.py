import os
from typing import Dict, Optional
from uuid import uuid4

from src.domain.models.user import User, UserStatus
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.errors import InvalidCredentialsError, UserNotFoundError
from src.domain.models.user_creation_request import UserCreationRequest
from datetime import datetime, timedelta
import hashlib

class InMemoryUserRepositoryAdapter(UserRepositoryPort):
    """In-memory implementation of UserRepository."""

    memory_store: Dict[int, User] = {}
    tokens_store: Dict[str, int] = {}

    def sequence(self) -> int:
        """Generate a new sequence number."""
        return str(len(self.memory_store) + 1)

    def create(self, userDto: UserCreationRequest) -> User:
        """Create a new user."""
        time_now = datetime.now().isoformat(timespec="seconds")
        time_in_1_hour = (datetime.now() + timedelta(hours=1)).isoformat(timespec="seconds")
        salt = os.urandom(16).hex()
        password_hash = hashlib.sha256((userDto.password + salt).encode()).hexdigest()

        user = User(
            id=self.sequence(),
            username=userDto.username,
            email=userDto.email,
            phoneNumber=userDto.phoneNumber,
            dni=userDto.dni,
            fullName=userDto.fullName,
            password=password_hash,
            salt=salt,
            token=str(uuid4()),
            status=UserStatus.NOT_VERIFIED,
            expireAt=time_in_1_hour,
            createdAt=time_now,
            updatedAt=time_now
        )

        self.memory_store[user.id] = user
        self.tokens_store[user.token] = user.id

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
        raise InvalidCredentialsError("Invalid username or password")

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
