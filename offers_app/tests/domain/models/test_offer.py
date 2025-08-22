from src.domain.models.offer import Offer

def test_create_user_with_valid_data(valid_offer_data):
    """Test creating an offer with valid data."""
    offer = Offer(**valid_offer_data)
    assert offer.id is None  # ID should be None initially
    assert offer.postId == valid_offer_data["postId"]
    assert offer.userId == valid_offer_data["userId"]
    assert offer.description == valid_offer_data["description"]
    assert offer.size == valid_offer_data["size"]
    assert offer.fragile == valid_offer_data["fragile"]
    assert offer.offer == valid_offer_data["offer"]
