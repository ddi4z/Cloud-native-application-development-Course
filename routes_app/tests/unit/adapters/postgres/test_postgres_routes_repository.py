import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from routes_app.domain.models.models import Trayecto
from routes_app.adapters.postgres.routes_repository_adapter import (
    PostgresRoutesRepositoryAdapter,
)
from routes_app.errors import TrayectoNotFoundError, FlightIdAlreadyExistsError
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def trayecto_domain_model():
    """Crea una instancia del modelo de dominio Trayecto para las pruebas."""
    now = datetime.now(timezone.utc)
    return Trayecto(
        id=uuid4(),
        flightId="AV456",
        sourceAirportCode="JFK",
        sourceCountry="USA",
        destinyAirportCode="LHR",
        destinyCountry="UK",
        bagCost=70,
        plannedStartDate=now + timedelta(days=5),
        plannedEndDate=now + timedelta(days=6),
    )


@pytest.fixture
def mock_session():
    """Crea un mock de la sesión de SQLAlchemy."""
    return MagicMock()


@patch("routes_app.adapters.postgres.routes_repository_adapter.create_engine")
def test_create_trayecto_success(
    mock_create_engine, mock_session, trayecto_domain_model, mocker
):
    """
    Prueba la creación exitosa de un trayecto en el adaptador de PostgreSQL.
    """
    # Simula la variable de entorno ANTES de crear el adaptador
    mocker.patch.dict(
        "os.environ", {"DATABASE_URL": "postgresql://test:test@localhost/testdb"}
    )

    adapter = PostgresRoutesRepositoryAdapter()
    adapter._get_session = MagicMock(return_value=mock_session)
    mock_session.__enter__.return_value = mock_session

    result = adapter.create(trayecto_domain_model)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.flightId == trayecto_domain_model.flightId


@patch("routes_app.adapters.postgres.routes_repository_adapter.create_engine")
def test_create_trayecto_with_existing_flightid_fails(
    mock_create_engine, mock_session, trayecto_domain_model, mocker
):  # <-- AÑADIDO mocker
    """
    Prueba que la creación de un trayecto falle si el flightId ya existe,
    lanzando la excepción correcta.
    """
    mocker.patch.dict(
        "os.environ", {"DATABASE_URL": "postgresql://test:test@localhost/testdb"}
    )
    adapter = PostgresRoutesRepositoryAdapter()
    adapter._get_session = MagicMock(return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    mock_session.commit.side_effect = IntegrityError(
        "mocked error", params=None, orig=None
    )

    with pytest.raises(FlightIdAlreadyExistsError):
        adapter.create(trayecto_domain_model)

    mock_session.rollback.assert_called_once()


@patch("routes_app.adapters.postgres.routes_repository_adapter.create_engine")
def test_get_trayecto_not_found(
    mock_create_engine, mock_session, mocker
):  # <-- AÑADIDO mocker
    """
    Prueba que se lance TrayectoNotFoundError cuando se busca un trayecto que no existe.
    """
    # Simula la variable de entorno ANTES de crear el adaptador
    mocker.patch.dict(
        "os.environ", {"DATABASE_URL": "postgresql://test:test@localhost/testdb"}
    )
    adapter = PostgresRoutesRepositoryAdapter()
    adapter._get_session = MagicMock(return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(TrayectoNotFoundError):
        adapter.get(uuid4())
