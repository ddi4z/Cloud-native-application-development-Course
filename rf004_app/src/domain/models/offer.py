from pydantic import BaseModel
from enum import Enum


class OfferSize(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"


class Offer(BaseModel):
    """Offer domain model."""

    description: str
    size: OfferSize
    fragile: bool
    offer: int


class CreatedOffer(BaseModel):
    """Created offer domain model."""

    id: str
    userId: str
    createdAt: str
