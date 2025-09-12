import pytest

from src.domain.models.score_db import ScoreDB
from sqlalchemy import inspect

def test_table_created(session):
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    assert "scores" in tables


def test_insert_and_query_score(session):
    score = ScoreDB(offer_id="offer1", value=123.45)
    session.add(score)
    session.commit()

    result = session.query(ScoreDB).filter_by(offer_id="offer1").first()
    assert result is not None
    assert result.offer_id == "offer1"
    assert result.value == 123.45

def test_value_cannot_be_null(session):
    score = ScoreDB(offer_id="offer3", value=None)
    session.add(score)
    with pytest.raises(Exception):
        session.commit() 
