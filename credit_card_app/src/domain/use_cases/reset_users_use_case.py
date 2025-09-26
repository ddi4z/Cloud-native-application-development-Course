from src.domain.models.user import User
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class ResetUsersUseCase(BaseUseCase):
    """Use case for deleting all users."""

    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self) -> dict:
        """Delete all users and return a confirmation message."""
        return self.user_repository.reset()
