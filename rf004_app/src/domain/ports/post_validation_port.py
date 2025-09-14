from abc import abstractmethod
from typing import Optional
from src.domain.models.post import Post

from .http_request import HttpRequest


class PostValidationPort(HttpRequest):
    """Post validation interface."""

    @abstractmethod
    def validate_and_get_post(self, postId: str) -> Optional[Post]:
        """Validate and get the post from the service."""
        raise NotImplementedError("This method should be overridden in subclasses")
