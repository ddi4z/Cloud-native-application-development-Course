import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import uuid4

from src.domain.models.user import User, UserStatus
from src.domain.models.user_creation_request import UserCreationRequest
from src.domain.models.user_update_request import UserUpdateRequest
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.errors import (
    InvalidCredentialsError,
    InvalidTokenError,
    MissingTokenError,
    MissingUserInformationError,
    UnauthorizedUserStatusError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.domain.models.user_callback_request import UserCallbackRequest


class InMemoryUserRepositoryAdapter(UserRepositoryPort):
    """In-memory implementation of UserRepository."""

    memory_store: Dict[int, User] = {}
    tokens_store: Dict[str, int] = {}

    def sequence(self) -> int:
        """Generate a new sequence number."""
        return str(len(self.memory_store) + 1)

    def generate_expiration_time(self, time_now: str) -> str:
        return (datetime.fromisoformat(time_now) + timedelta(hours=1)).isoformat(
            timespec="seconds"
        )

    def create(self, user_dto: UserCreationRequest) -> User:
        """Create a new user."""

        if not all([user_dto.username, user_dto.password, user_dto.email]):
            raise MissingUserInformationError(
                "Username, password, and email are required."
            )

        for user in self.memory_store.values():
            if user.username == user_dto.username or user.email == user_dto.email:
                raise UserAlreadyExistsError("Username or email already exists.")

        time_now = datetime.now().isoformat(timespec="seconds")
        time_in_1_hour = self.generate_expiration_time(time_now)

        salt = os.urandom(16).hex()
        password_hash = hashlib.sha256((user_dto.password + salt).encode()).hexdigest()

        user = User(
            id=self.sequence(),
            username=user_dto.username,
            email=user_dto.email,
            phoneNumber=user_dto.phoneNumber,
            dni=user_dto.dni,
            fullName=user_dto.fullName,
            password=password_hash,
            salt=salt,
            token=str(uuid4()),
            status=UserStatus.PENDING_VERIFICATION,
            expireAt=time_in_1_hour,
            createdAt=time_now,
            updatedAt=time_now,
        )

        self.memory_store[user.id] = user
        self.tokens_store[user.token] = user.id

        return user

    def update(self, user_id: str, update_data: UserUpdateRequest) -> User:
        """Update an existing user by ID."""
        if user_id not in self.memory_store:
            raise UserNotFoundError(f"User with id {user_id} not found.")
        if not any(
            [
                update_data.status,
                update_data.dni,
                update_data.fullName,
                update_data.phoneNumber,
            ]
        ):
            raise MissingUserInformationError(
                "At least one field must be provided for update."
            )
        user = self.memory_store[user_id]
        for key, value in update_data.dict(exclude_none=True).items():
            setattr(user, key, value)
        user.updatedAt = datetime.now().isoformat(timespec="seconds")
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        if not all([username, password]):
            raise MissingUserInformationError("Username and password are required.")
        for user in self.memory_store.values():
            salted_password = hashlib.sha256(
                (password + user.salt).encode()
            ).hexdigest()
            if user.username == username and user.password == salted_password:
                if user.status != UserStatus.VERIFIED:
                    raise UnauthorizedUserStatusError(
                        "User status does not allow authentication."
                    )

                token = str(uuid4())
                time_now = datetime.now().isoformat(timespec="seconds")
                expire_at = self.generate_expiration_time(time_now)

                old_token = user.token
                del self.tokens_store[old_token]

                user.token = token
                user.expireAt = expire_at
                user.updatedAt = time_now

                self.tokens_store[token] = user.id
                return user
        raise InvalidCredentialsError("Invalid username or password.")

    def get_current_user(self, token: Optional[str]) -> Optional[User]:
        if not token:
            raise MissingTokenError("Token is missing from the request header.")
        user_id = self.tokens_store.get(token)

        if not user_id:
            raise InvalidTokenError("The token is invalid or has expired.")

        user = self.memory_store.get(user_id)
        if not user or user.expireAt < datetime.now().isoformat(timespec="seconds"):
            raise InvalidTokenError("The token is invalid or has expired.")
        return user

    def count(self) -> int:
        """Get total number of users."""
        return len(self.memory_store)

    def reset(self) -> None:
        """Delete all users."""
        self.memory_store.clear()
        self.tokens_store.clear()

    def patch(self, user_id: str, callback_data: UserCallbackRequest) -> User:
        SECRET_TOKEN = os.getenv("SECRET_TOKEN")
        RUV = callback_data.RUV
        SCORE = callback_data.score

        token = f"{SECRET_TOKEN}:{RUV}:{SCORE}"
        sha_token = hashlib.sha256(token.encode()).hexdigest()
        assert sha_token == callback_data.verifyToken

        return self.update(user_id, UserUpdateRequest(status=UserStatus.VERIFIED))
