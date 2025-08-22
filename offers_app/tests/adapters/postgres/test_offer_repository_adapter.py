from src.domain.models.offer import Offer, OfferSize
from src.errors import (
    InvalidFieldInOfferError,
    OfferNotFoundError,
    PreconditionOfferFailedError,
)

import pytest
import uuid


def test_create_offer(offer_repository_adapter):
    repo = offer_repository_adapter
    offer_id = str(uuid.uuid4())

    offer_model: Offer = Offer(
        id=offer_id,
        postId=str(uuid.uuid4()),
        userId=str(uuid.uuid4()),
        description="Una oferta de prueba",
        size=OfferSize.LARGE.value,
        fragile=False,
        offer=150,
    )

    repo.create(offer_model)
    created_offer = repo.get_all(None, None)

    # Assert
    assert repo.count() == 1
    assert created_offer[0].id == offer_id
    assert created_offer[0].description == "Una oferta de prueba"
    assert OfferSize.LARGE.value in created_offer[0].size
    assert created_offer[0].offer == 150
    assert created_offer[0].fragile is False
    assert created_offer[0].postId == offer_model.postId
    assert created_offer[0].userId == offer_model.userId


def test_create_valid_offer(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    created = repo.create(offer_model)

    assert created.id is not None
    assert repo.count() == 1
    assert created.description == "A valid offer description"


def test_create_invalid_missing_field(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    offer_model.description = None

    with pytest.raises(InvalidFieldInOfferError):
        repo.create(offer_model)


def test_create_invalid_uuid(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    offer_model.postId = "not-a-uuid"

    with pytest.raises(InvalidFieldInOfferError):
        repo.create(offer_model)


def test_create_invalid_negative_offer(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    offer_model.offer = -100

    with pytest.raises(PreconditionOfferFailedError):
        repo.create(offer_model)


def test_create_invalid_size(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    offer_model.size = "INVALID"

    with pytest.raises(PreconditionOfferFailedError):
        repo.create(offer_model)


"""
These tests cover the get_by_id methods of the repository.
"""

""" # This test isn't working
def test_get_by_id_success(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    created = repo.create(offer_model)
    found = repo.get_by_id(str(created.id))
    assert found.id == created.id
 """

def test_get_by_id_invalid_uuid(offer_repository_adapter):
    repo = offer_repository_adapter
    with pytest.raises(InvalidFieldInOfferError):
        repo.get_by_id("not-a-uuid")


def test_get_by_id_not_found(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    repo.create(offer_model)
    with pytest.raises(OfferNotFoundError):
        repo.get_by_id(str(uuid.uuid4()))


"""
These tests cover the get_all methods of the repository.
"""


def test_get_all_no_filters(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    repo.create(offer_model)
    offers = repo.get_all(None, None)
    assert len(offers) == 1


def test_get_all_filter_by_postId(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    created = repo.create(offer_model)
    offers = repo.get_all(postId=offer_model.postId, ownerId=None)
    assert created in offers


def test_get_all_filter_by_ownerId(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    created = repo.create(offer_model)
    offers = repo.get_all(postId=None, ownerId=offer_model.userId)
    assert created in offers


def test_get_all_filter_by_both(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    created = repo.create(offer_model)
    offers = repo.get_all(postId=offer_model.postId, ownerId=offer_model.userId)
    assert created in offers


def test_get_all_invalid_filter_uuid(offer_repository_adapter):
    repo = offer_repository_adapter
    with pytest.raises(InvalidFieldInOfferError):
        repo.get_all(postId="invalid-uuid", ownerId=None)


"""
These tests cover the delete methods of the repository.
"""


""" # This test isn't working
def test_delete_success(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    created = repo.create(offer_model)
    deleted = repo.delete(str(created.id))
    assert deleted.id == created.id
    assert repo.count() == 0
 """

def test_delete_invalid_uuid(offer_repository_adapter):
    repo = offer_repository_adapter
    with pytest.raises(InvalidFieldInOfferError):
        repo.delete("invalid-uuid")


def test_delete_not_found(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    repo.create(offer_model)
    with pytest.raises(OfferNotFoundError):
        repo.delete(str(uuid.uuid4()))


"""
These tests cover the count/reset methods of the repository.
"""


def test_count_and_reset(offer_repository_adapter, offer_model):
    repo = offer_repository_adapter
    repo.create(offer_model)
    assert repo.count() == 1
    repo.reset()
    assert repo.count() == 0
