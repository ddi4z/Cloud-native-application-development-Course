from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class ResetPostUseCase(BaseUseCase):
    """Use case for deleting all posts"""

    def __init__(self, post_repository: PostRepositoryPort):
        self.post_repository = post_repository

    def execute(self) -> dict:
        """Delete all posts and return a confirmation message."""
        return self.post_repository.reset()
