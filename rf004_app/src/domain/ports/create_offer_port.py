from abc import abstractmethod, ABC
from typing import Optional
from src.domain.models.offer import Offer, CreatedOffer


class CreateOfferPort(ABC):
    """Offer repository interface."""

    @abstractmethod
    def create_offer(self, offer: Offer, userId: str, postId: str) -> Optional[CreatedOffer]:
        """Create a new offer."""
        raise NotImplementedError("This method should be overridden in subclasses")
