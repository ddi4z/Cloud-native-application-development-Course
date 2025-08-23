import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from routes_app.domain.models.models import Trayecto
from routes_app.adapters.memory.routes_repository_adapter import InMemoryRoutesRepositoryAdapter
from routes_app.errors import TrayectoNotFoundError, FlightIdAlreadyExistsError

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
def memory_adapter():
    """
    Devuelve un adaptador in-memory limpio por prueba.
    Si tu implementación usa un store estático, asegúrate de limpiarlo aquí.
    """
    adapter = InMemoryRoutesRepositoryAdapter()
    return adapter


def test_create_trayecto_success(memory_adapter, trayecto_domain_model):
    """
    Prueba la creación exitosa de un trayecto en el adaptador in memory.
    """
    created = memory_adapter.create(trayecto_domain_model)

    assert created.flightId == trayecto_domain_model.flightId
    fetched = memory_adapter.get(created.id)
    assert fetched == created


def test_create_trayecto_with_existing_flightid_fails(memory_adapter, trayecto_domain_model):
    """
    Prueba que la creación falle si el flightId ya existe, lanzando la excepción correcta.
    """
    memory_adapter.create(trayecto_domain_model)

    # Mismo flightId, id distinto
    duplicate = Trayecto(**{**trayecto_domain_model.model_dump(), "id": uuid4()})

    with pytest.raises(FlightIdAlreadyExistsError):
        memory_adapter.create(duplicate)


def test_get_trayecto_success(memory_adapter, trayecto_domain_model):
    """
    Prueba obtener un trayecto existente por id.
    """
    created = memory_adapter.create(trayecto_domain_model)
    fetched = memory_adapter.get(created.id)

    assert fetched.id == created.id
    assert fetched.flightId == created.flightId
    assert fetched.sourceAirportCode == created.sourceAirportCode
    assert fetched.destinyAirportCode == created.destinyAirportCode
    assert fetched.bagCost == created.bagCost
    assert fetched.plannedStartDate == created.plannedStartDate
    assert fetched.plannedEndDate == created.plannedEndDate


def test_get_trayecto_not_found(memory_adapter):
    """
    Prueba que se lance TrayectoNotFoundError cuando se busca un trayecto que no existe.
    """
    with pytest.raises(TrayectoNotFoundError):
        memory_adapter.get(uuid4())