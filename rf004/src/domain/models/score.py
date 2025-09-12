from pydantic import BaseModel


class Score(BaseModel):
    """Score domain model."""

    score: float
    offerId: str
    postId: str
