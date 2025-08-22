import uuid

from src.entrypoints.api.dtos.created_offer_dto import CreatedOfferDto


def test_created_offer_dto(valid_created_offer_dto_data):
    """Test creating a CreatedOfferDto with valid data."""
    dto = CreatedOfferDto(**valid_created_offer_dto_data)

    assert dto.userId == valid_created_offer_dto_data["userId"]
    assert dto.createdAt == valid_created_offer_dto_data["createdAt"]
    assert str(dto.id) == valid_created_offer_dto_data["id"]

    assert dto.id is not None
    assert isinstance(dto.id, uuid.UUID)
