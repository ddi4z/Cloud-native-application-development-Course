from datetime import datetime

from src.domain.models.posts import Post
from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase

class CreatePostUseCase(BaseUseCase):
    """Use case for creating a post"""

    def __init__(self, post_repository: PostRepositoryPort):
        self.post_repository = post_repository      

    def execute(self, routeId:str, expireAt:datetime, owner:str) -> Post:
        """Filter posts matching a certain criteria."""
        return self.post_repository.filter(routeId,expireAt,owner)