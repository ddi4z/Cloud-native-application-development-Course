from src.domain.models.user import User
from src.domain.models.user_callback_request import UserCallbackRequest
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class PatchUserUseCase(BaseUseCase):
    """Use case for patching a user."""

    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, user_id: str, user: UserCallbackRequest) -> User:
        """Patch an existing user."""
        return self.user_repository.patch(user_id, user)
