from pydantic import BaseModel


class Score(BaseModel):
    """Score domain model."""

    userId: str
    offerId: str
    postId: str
    size: str
    amountOffered: int
