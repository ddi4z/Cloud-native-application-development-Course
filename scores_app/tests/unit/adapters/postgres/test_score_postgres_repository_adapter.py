import os
import pytest


from src.adapters.postgres.score_repository_adapter import PostgresScoreRepositoryAdapter
from src.domain.models.score_request import ScoreRequest
from src.domain.models.score_db import ScoreDB
from src.errors import InvalidSizeError




def test_init_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL not set"):
        PostgresScoreRepositoryAdapter()


def test_calculate_creates_new_score(repo):
    request = ScoreRequest(
        offer_id="offer1",
        size="MEDIANO",
        amount_offered=100,
        baggage_value=40,
    )

    result = repo.calculate(request)

    assert isinstance(result, (int, float))
    assert result == 100 - (0.5 * 40)

    with repo._get_session() as db:
        saved = db.query(ScoreDB).filter_by(offer_id="offer1").first()
        assert saved is not None
        assert saved.value == result


def test_calculate_updates_existing_score(repo):
    request = ScoreRequest(
        offer_id="offer2",
        size="SMALL",
        amount_offered=200,
        baggage_value=100,
    )
    repo.calculate(request)

    request2 = ScoreRequest(
        offer_id="offer2",
        size="LARGE",
        amount_offered=300,
        baggage_value=50,
    )
    result2 = repo.calculate(request2)

    with repo._get_session() as db:
        saved = db.query(ScoreDB).filter_by(offer_id="offer2").first()
        assert saved.value == result2
        assert result2 == 300 - (1 * 50) 


def test_calculate_invalid_size_raises(repo):
    request = ScoreRequest(
        offer_id="offer3",
        size="INVALIDO",
        amount_offered=100,
        baggage_value=20,
    )

    with pytest.raises(InvalidSizeError):
        repo.calculate(request)
