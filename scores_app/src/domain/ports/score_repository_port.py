from abc import ABC, abstractmethod
from src.domain.models.score_request import ScoreRequest


class ScoreRepositoryPort(ABC):
    """User repository interface."""

    @abstractmethod
    def calculate(self, scoreRequest: ScoreRequest) -> int:
        """Set a score."""
        pass