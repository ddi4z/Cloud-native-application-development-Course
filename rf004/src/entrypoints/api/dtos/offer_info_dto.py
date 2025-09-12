from pydantic import BaseModel

from src.domain.models.offer import Offer, OfferSize

class OfferInfoDto(BaseModel):
    """Offer info passed through HTTP."""
    description: str = None
    size: str = None
    fragile: bool = None
    offer: int = None

    @classmethod
    def to_domain(self):
        """Convert to domain model."""
        return Offer(
            description=self.description,
            size=OfferSize(self.size),
            fragile=self.fragile,
            offer=self.offer,
        )
