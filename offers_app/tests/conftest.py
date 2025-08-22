import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.memory.offer_repository_adapter import InMemoryOfferRepositoryAdapter
from src.adapters.postgres.models import Base
from src.adapters.postgres.offer_repository_adapter import (
    PostgresOfferRepositoryAdapter,
)
from src.domain.models.offer import Offer, OfferSize


@pytest.fixture
def valid_offer_data():
    """Fixture providing valid offer data."""
    return {
        "postId": str(uuid.uuid4()),
        "userId": str(uuid.uuid4()),
        "description": "A valid offer description",
        "size": "LARGE",
        "fragile": True,
        "offer": 100,
    }


@pytest.fixture
def valid_created_offer_dto_data():
    """Fixture providing valid created offer DTO data."""
    return {
        "id": str(uuid.uuid4()),
        "userId": str(uuid.uuid4()),
        "createdAt": "2023-10-01T12:00:00",
    }


# Unused but could be useful for some tests
@pytest.fixture
def offer_with_id():
    """Fixture providing a offer with ID."""
    return Offer(
        id=str(uuid.uuid4()),
        postId=str(uuid.uuid4()),
        userId=str(uuid.uuid4()),
        description="A valid offer description",
        size=str(OfferSize.LARGE),
        fragile=True,
        offer=100,
    )


@pytest.fixture
def offer_model(valid_offer_data):
    """Fixture providing a Offer model instance."""
    return Offer(**valid_offer_data)


@pytest.fixture
def repo():
    adapter = InMemoryOfferRepositoryAdapter()
    adapter.reset()
    return adapter


# This fixture sets up an in-memory SQLite database for testing purposes.


@pytest.fixture(scope="session")
def engine():
    """Crea un engine de SQLite en memoria para toda la sesión de pruebas."""
    return create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=sqlalchemy.pool.StaticPool,
    )


@pytest.fixture(scope="session")
def tables(engine):
    """Crea y elimina las tablas en la BD de pruebas."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """
    Crea una sesión de base de datos aislada por test.
    Cada test corre en su propia transacción que se hace rollback al final.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, expire_on_commit=False)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def offer_repository_adapter(db_session):
    """
    Devuelve un repositorio de ofertas conectado a SQLite en memoria.
    """
    return PostgresOfferRepositoryAdapter(session_factory=lambda: db_session)
