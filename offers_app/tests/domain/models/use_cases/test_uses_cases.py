import uuid

import pytest

from src.adapters.memory.offer_repository_adapter import InMemoryOfferRepositoryAdapter
from src.domain.models.offer import Offer, OfferSize
from src.domain.use_cases.count_offers_use_case import CountOffersUseCase
from src.domain.use_cases.create_offer_use_case import CreateOfferUseCase
from src.domain.use_cases.delete_offer_use_case import DeleteOfferUseCase
from src.domain.use_cases.get_offer_use_case import GetOfferUseCase
from src.domain.use_cases.get_offers_use_case import GetAllOffersUseCase
from src.domain.use_cases.reset_offers_use_case import ResetOffersUseCase


def make_offer(**kwargs):
    return Offer(
        id=str(uuid.uuid4()),
        postId=str(uuid.uuid4()),
        userId=str(uuid.uuid4()),
        description=kwargs.get("description", "test offer"),
        size=kwargs.get("size", OfferSize.SMALL.value),
        fragile=kwargs.get("fragile", False),
        offer=kwargs.get("offer", 100),
    )


@pytest.fixture
def repo():
    return InMemoryOfferRepositoryAdapter()


def test_create_offer(repo):
    offer = make_offer()
    created = CreateOfferUseCase(repo).execute(offer)
    assert created.id == offer.id
    assert created.postId == offer.postId
    assert created.userId == offer.userId
    assert created.description == offer.description
    assert created.size == offer.size
    assert created.fragile == offer.fragile
    assert created.offer == offer.offer


def get_offer_by_id(repo):
    repo.reset()
    offer = make_offer()
    CreateOfferUseCase(repo).execute(offer)

    fetched = GetOfferUseCase(repo).execute(offer.id)
    assert fetched is not None
    assert fetched.id == offer.id
    assert fetched.postId == offer.postId
    assert fetched.userId == offer.userId
    assert fetched.description == offer.description
    assert fetched.size == offer.size
    assert fetched.fragile == offer.fragile
    assert fetched.offer == offer.offer


def test_get_offerst(repo):
    # inicialmente vacío
    repo.reset()

    assert CountOffersUseCase(repo).execute() == 0

    offer1 = make_offer(description="uno")
    offer2 = make_offer(description="dos")
    CreateOfferUseCase(repo).execute(offer1)
    CreateOfferUseCase(repo).execute(offer2)

    offers = GetAllOffersUseCase(repo).execute(None, None)
    assert len(offers) == 2
    assert CountOffersUseCase(repo).execute() == 2


def test_delete_offer(repo):
    repo.reset()
    assert CountOffersUseCase(repo).execute() == 0

    offer = make_offer()
    CreateOfferUseCase(repo).execute(offer)
    assert CountOffersUseCase(repo).execute() == 1

    DeleteOfferUseCase(repo).execute(str(offer.id))
    assert CountOffersUseCase(repo).execute() == 0


def test_reset_offers(repo):
    repo.reset()

    CreateOfferUseCase(repo).execute(make_offer())
    CreateOfferUseCase(repo).execute(make_offer())
    assert CountOffersUseCase(repo).execute() == 2

    ResetOffersUseCase(repo).execute()
    assert CountOffersUseCase(repo).execute() == 0
