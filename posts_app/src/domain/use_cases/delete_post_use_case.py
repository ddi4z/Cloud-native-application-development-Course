from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase
from uuid import UUID

class DeletePostUseCase(BaseUseCase):
    """Use case for creating a post"""

    def __init__(self, post_repository: PostRepositoryPort):
        self.post_repository = post_repository      

    def execute(self, id:UUID) -> dict:
        """Delete a post and return a confirmation message."""
        return self.post_repository.delete(id)