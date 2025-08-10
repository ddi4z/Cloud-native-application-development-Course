import datetime
from enum import Enum

from pydantic import BaseModel, Field


class OfferSize(str, Enum):
    """Enum for offer sizes."""

    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"


class Offer(BaseModel):
    """Offer domain model."""

    id: int | None = None
    postId: str = Field(
        description="Post ID must be a string",
        example="9655dd8d-22e6-4bc6-bc8d-1661a5a42c37",
    )
    userId: str = Field(
        description="User ID must be a string",
        example="9655dd8d-22e6-4bc6-bc8d-1661a5a42c37",
    )


    description: str = Field(
        min_length=1,
        max_length=140,
        description="Description cannot be empty and must be less than 140 characters"
    )
    size: OfferSize
    fragile: bool = Field(description="Fragile must be a boolean value", default=False)
    offer: int = Field(description="Offer must be a positive integer", ge=0)
    # Date and hour of the offer creation
    createdAt: str = Field(
        description="Creation date of the offer",
        default_factory=lambda: datetime.datetime.now().isoformat(
            timespec="seconds"
        ),
        example="2023-10-01T12:00:00",
    )
