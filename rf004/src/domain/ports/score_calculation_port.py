from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models.score import Score


class ScoreCalculationPort(ABC):
    """Score calculation port."""

    @abstractmethod
    def calculate_score(self, postId: str, offerSize: str) -> Optional[Score]:
        """Calculate the score of a given offer."""
        raise NotImplementedError("This method should be overridden in subclasses")
