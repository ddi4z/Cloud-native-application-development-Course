from pydantic import BaseModel

from src.domain.models.offer import CreatedOffer

class CreatedOfferInfoDto(BaseModel):
    """Offer domain model."""
    id:  str = None
    userId: str = None
    createdAt: str = None
    postId: str = None

    @classmethod
    def from_domain(cls, created_offer: CreatedOffer, postId: str) -> "CreatedOfferInfoDto":
        return cls(**created_offer.model_dump(), postId=postId)
