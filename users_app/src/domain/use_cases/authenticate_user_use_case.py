from src.domain.models.user import User
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase

class AuthenticateUserUseCase(BaseUseCase):
    """Use case for authenticating a user."""

    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, username: str, password: str) -> User:
        """Authenticate a user by username and password."""
        return self.user_repository.authenticate(username, password)