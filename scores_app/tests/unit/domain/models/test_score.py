import pytest
from pydantic import ValidationError

from src.domain.models.score import Score


def test_score_valid():
    score = Score(offer_id="123e4567-e89b-12d3-a456-426614174001", value=85)
    assert score.offer_id == "123e4567-e89b-12d3-a456-426614174001"
    assert score.value == 85


def test_invalid_value_type():
    with pytest.raises(ValidationError) as excinfo:
        Score(offer_id="offer123", value="not-an-int")
    assert "value" in str(excinfo.value)


def test_invalid_offer_id_type():
    with pytest.raises(ValidationError) as excinfo:
        Score(offer_id=123, value=50)
    assert "offer_id" in str(excinfo.value)


def test_extra_fields_are_ignored_by_default():
    score = Score(offer_id="offerX", value=10, extra_field="ignored")
    assert not hasattr(score, "extra_field")
    assert score.offer_id == "offerX"
    assert score.value == 10
