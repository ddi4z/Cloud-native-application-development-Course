from users_app.src.domain.models.user import User
from domain.ports.user_repository_port import UserRepositoryPort
from domain.use_cases.base_use_case import BaseUseCase


class CreateUserUseCase(BaseUseCase):
    """Use case for creating a user."""

    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, user: User) -> User:
        """Create a new user."""
        return self.user_repository.create(user)
