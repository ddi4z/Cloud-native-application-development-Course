from users_app.src.domain.models.user import User
from domain.ports.user_repository_port import UserRepositoryPort
from domain.use_cases.base_use_case import BaseUseCase

class GetUsersCountUseCase(BaseUseCase):
    """Use case for getting the total number of users."""

    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self) -> int:
        """Get the count of all users."""
        return self.user_repository.count()