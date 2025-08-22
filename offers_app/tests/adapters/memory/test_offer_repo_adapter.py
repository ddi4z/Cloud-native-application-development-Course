import pytest
from src.errors import (
    InvalidFieldInOfferError,
    PreconditionOfferFailedError,
    OfferNotFoundError,
)
import uuid

def test_create_valid_offer(repo, offer_model):
    created = repo.create(offer_model)
    assert created.id is not None
    assert repo.count() == 1
    assert created.description == "A valid offer description"


def test_create_invalid_missing_field(repo, offer_model):
    setattr(offer_model, "description", None)

    with pytest.raises(InvalidFieldInOfferError):
        repo.create(offer_model)


def test_create_invalid_uuid(repo, offer_model):
    offer_model.postId = "not-a-uuid"
    with pytest.raises(InvalidFieldInOfferError):
        repo.create(offer_model)


def test_create_invalid_negative_offer(repo, offer_model):
    setattr(offer_model, "offer", -100)

    with pytest.raises(PreconditionOfferFailedError):
        repo.create(offer_model)


def test_create_invalid_size(repo, offer_model):
    offer_model.size = "INVALID"
    with pytest.raises(PreconditionOfferFailedError):
        repo.create(offer_model)

"""
These tests cover the get_by_id methods of the repository.
"""

def test_get_by_id_success(repo, offer_model):
    created = repo.create(offer_model)
    found = repo.get_by_id(str(created.id))
    assert found.id == created.id


def test_get_by_id_invalid_uuid(repo):
    with pytest.raises(InvalidFieldInOfferError):
        repo.get_by_id("not-a-uuid")


def test_get_by_id_not_found(repo, offer_model):
    repo.create(offer_model)
    with pytest.raises(OfferNotFoundError):
        repo.get_by_id(str(uuid.uuid4()))

"""
These tests cover the get_all methods of the repository.
"""

def test_get_all_no_filters(repo, offer_model):
    repo.create(offer_model)
    offers = repo.get_all(None, None)
    assert len(offers) == 1


def test_get_all_filter_by_postId(repo, offer_model):
    created = repo.create(offer_model)
    offers = repo.get_all(postId=offer_model.postId, ownerId=None)
    assert created in offers


def test_get_all_filter_by_ownerId(repo, offer_model):
    created = repo.create(offer_model)
    offers = repo.get_all(postId=None, ownerId=offer_model.userId)
    assert created in offers


def test_get_all_filter_by_both(repo, offer_model):
    created = repo.create(offer_model)
    offers = repo.get_all(postId=offer_model.postId, ownerId=offer_model.userId)
    assert created in offers


def test_get_all_invalid_filter_uuid(repo):
    with pytest.raises(InvalidFieldInOfferError):
        repo.get_all(postId="invalid-uuid", ownerId=None)

"""
These tests cover the delete methods of the repository.
"""

def test_delete_success(repo, offer_model):
    created = repo.create(offer_model)
    deleted = repo.delete(str(created.id))
    assert deleted.id == created.id
    assert repo.count() == 0


def test_delete_invalid_uuid(repo):
    with pytest.raises(InvalidFieldInOfferError):
        repo.delete("invalid-uuid")


def test_delete_not_found(repo, offer_model):
    repo.create(offer_model)
    with pytest.raises(OfferNotFoundError):
        repo.delete(str(uuid.uuid4()))

"""
These tests cover the delete methods of the repository.
"""
def test_count_and_reset(repo, offer_model):
    repo.create(offer_model)
    assert repo.count() == 1
    repo.reset()
    assert repo.count() == 0
