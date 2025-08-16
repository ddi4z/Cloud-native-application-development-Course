from abc import ABC, abstractmethod
from typing import Optional, Protocol, List
from uuid import UUID
from datetime import datetime, timezone

from src.domain.models.posts import Post


class PostRepositoryPort(ABC):
    """User repository interface."""

    @abstractmethod
    def create(self, routeId:str, expireAt:datetime, userId:str) -> Post:
        """Create a new post."""
        pass

    @abstractmethod
    def filter(self, routeId:str, expireAt:datetime, owner:str) -> Post:
        """Filter posts matching certain criteria."""
        pass

    @abstractmethod
    def query(self, id: str) -> Optional[Post]:
        """Get information from a specific post."""
        pass

    @abstractmethod
    def delete(self, id:UUID) -> None:
        """Delete a post from the database."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count existing posts in database."""
        pass

    @abstractmethod
    def ping(self) -> str:
        """Check service status."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Delete all posts in database."""
        pass

    
