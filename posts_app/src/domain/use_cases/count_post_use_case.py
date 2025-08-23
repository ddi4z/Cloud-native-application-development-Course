from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class CountPostUseCase(BaseUseCase):
    """Use case for getting total number of posts"""

    def __init__(self, post_repository: PostRepositoryPort):
        self.post_repository = post_repository

    def execute(self) -> int:
        """Count all posts in database."""
        return self.post_repository.count()
