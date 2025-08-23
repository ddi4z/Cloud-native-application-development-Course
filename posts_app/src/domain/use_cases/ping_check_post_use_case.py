from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class PingCheckPostUseCase(BaseUseCase):
    """Use case for repository check"""

    def __init__(self, post_repository: PostRepositoryPort):
        self.post_repository = post_repository

    def execute(self, id) -> bool:
        """Check status of post repository ."""
        return self.post_repository.ping()
