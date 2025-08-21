import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OfferSize(str, Enum):
    """Enum for offer sizes."""

    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"


class Offer(BaseModel):
    """Offer domain model."""

    id: Optional[str] = None
    postId: Optional[str] = None
    userId: Optional[str] = None

    description: Optional[str] = None
    size: Optional[str] = None
    fragile: Optional[bool] = None
    offer: Optional[int] = None

    # Date and hour of the offer creation
    createdAt: str = Field(
        description="Creation date of the offer",
        default_factory=lambda: datetime.datetime.now().isoformat(timespec="seconds"),
        example="2023-10-01T12:00:00",
    )
