from datetime import datetime
from typing import Dict, Optional, List
from uuid import UUID

from src.domain.models.posts import Post
from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase

class FilterPostUseCase(BaseUseCase):
    """Use case for creating a post"""

    def __init__(self, post_repository: PostRepositoryPort):
        self.post_repository = post_repository      

    def execute(self, expire: Optional[bool] = None, route:Optional[UUID] = None, owner:Optional[UUID] = None) -> dict:
        """Filter posts matching a certain criteria."""
        return self.post_repository.filter(expire,route,owner)