from abc import abstractmethod, ABC 
from typing import Optional
from src.domain.models.post import Post


class PostValidationPort(ABC):
    """Post validation interface."""

    @abstractmethod
    def validate_and_get_post(self, postId: str) -> Optional[Post]:
        """Validate and get the post from the service."""
        raise NotImplementedError("This method should be overridden in subclasses")
