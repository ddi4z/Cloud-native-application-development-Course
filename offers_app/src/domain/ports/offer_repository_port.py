from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.offer import Offer


class OfferRepositoryPort(ABC):
    """Offer repository interface."""

    @abstractmethod
    def create(self, offer: Offer) -> Offer:
        """Create a new offer."""
        pass

    @abstractmethod
    def get_by_id(self, offer_id: str) -> Optional[Offer]:
        """Get offer by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Offer]:
        """Get all offers."""
        pass

    @abstractmethod
    def delete(self, offer_id: str) -> Offer:
        """Delete a offer."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count the number of offers."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the offers repository."""
        pass