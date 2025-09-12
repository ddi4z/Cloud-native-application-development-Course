from abc import abstractmethod, ABC
from typing import Optional
from src.domain.models.score import Score


class ScoreCalculationPort(ABC):
    """Score calculation port."""

    @abstractmethod
    def calculate_score(self, score: Score) -> Optional[int]:
        """Calculate the score of a given offer."""
        raise NotImplementedError("This method should be overridden in subclasses")
