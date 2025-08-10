from src.domain.models.user import User
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase

class GetCurrentUserUseCase(BaseUseCase):
    """Use case for retrieving the current user."""

    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, token: str) -> User:
        """Retrieve current user from a token."""
        return self.user_repository.get_current_user(token)