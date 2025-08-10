from src.domain.models.user import User
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase

class UpdateUserUseCase(BaseUseCase):
    """Use case for updating a user."""

    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, user_id: str, user: User) -> User:
        """Update an existing user."""
        return self.user_repository.update(user_id, user)