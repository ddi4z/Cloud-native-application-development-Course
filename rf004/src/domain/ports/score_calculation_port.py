from abc import abstractmethod
from typing import Optional
from src.domain.models.score import Score

from .http_request_port import HttpRequestPort

class ScoreCalculationPort(HttpRequestPort):
    """Score calculation port."""

    @abstractmethod
    def calculate_score(self, postId: str, offerSize: str) -> Optional[Score]:
        """Calculate the score of a given offer."""
        raise NotImplementedError("This method should be overridden in subclasses")
