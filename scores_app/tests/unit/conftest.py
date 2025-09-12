import pytest
from src.adapters.postgres.score_repository_adapter import PostgresScoreRepositoryAdapter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models.score_db import Base
import pytest
from fastapi.testclient import TestClient

from src.entrypoints.api.routers.score_router import router 

@pytest.fixture(scope="function")
def repo(monkeypatch):
    test_url = "sqlite:///:memory:"
    monkeypatch.setenv("DATABASE_URL", test_url)

    adapter = PostgresScoreRepositoryAdapter()
    return adapter

@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    with TestingSessionLocal() as session:
        yield session
        
@pytest.fixture
def client():
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)