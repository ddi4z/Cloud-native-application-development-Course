from src.domain.models.score_request import ScoreRequest
from src.domain.ports.score_repository_port import ScoreRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class CalculateScoreUseCase(BaseUseCase):
    """Use case for creating a score."""

    def __init__(self, score_repository: ScoreRepositoryPort):
        self.score_repository = score_repository

    def execute(self, score_request: ScoreRequest) -> int:
        """Create a new score."""
        return self.score_repository.calculate(score_request)
