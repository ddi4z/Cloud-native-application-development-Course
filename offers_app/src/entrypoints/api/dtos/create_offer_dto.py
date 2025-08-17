from enum import Enum
from typing import Optional

from pydantic import BaseModel


class OfferSize(str, Enum):
    """Enum for offer sizes."""
    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"


class CreateOfferDto(BaseModel):
    """Offer domain model."""

    id: int | None = None
    postId: Optional[str]
    userId: Optional[str]

    description: Optional[str]
    size: Optional[OfferSize]
    fragile: Optional[bool]
    offer: Optional[int]
