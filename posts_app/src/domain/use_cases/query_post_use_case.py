from src.domain.models.posts import Post
from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class QueryPostUseCase(BaseUseCase):
    """Use case for creating a post"""

    def __init__(self, post_repository: PostRepositoryPort):
        self.post_repository = post_repository

    def execute(self, id) -> Post:
        """Get information on a post."""
        return self.post_repository.query(id)
