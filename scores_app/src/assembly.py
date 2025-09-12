from src.adapters.postgres.score_repository_adapter import PostgresScoreRepositoryAdapter
from src.domain.ports.score_repository_port import ScoreRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.calculate_score_use_case import CalculateScoreUseCase


# Shared in-memory repository instance for all score use cases
repository: ScoreRepositoryPort = PostgresScoreRepositoryAdapter()


def build_calculate_score_use_case() -> BaseUseCase:
    """Get create user use case."""
    return CalculateScoreUseCase(repository)
