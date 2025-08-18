import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from routes_app.domain.models.models import Trayecto
from routes_app.adapters.memory.routes_repository_adapter import InMemoryRoutesRepositoryAdapter

@pytest.fixture
def future_window():
    """Devuelve (inicio, fin) en el futuro con 24h de diferencia."""
    start = datetime.now(timezone.utc) + timedelta(hours=24)
    end = start + timedelta(hours=24)
    return start, end

@pytest.fixture
def valid_trayecto_data(future_window):
    start, end = future_window
    return {
        "id": uuid4(),
        "flightId": "FL123",
        "sourceAirportCode": "BOG",
        "sourceCountry": "CO",
        "destinyAirportCode": "MDE",
        "destinyCountry": "CO",
        "bagCost": 50,
        "plannedStartDate": start,
        "plannedEndDate": end,
    }

@pytest.fixture
def trayecto(valid_trayecto_data):
    """Instancia válida de Trayecto."""
    return Trayecto(**valid_trayecto_data)

@pytest.fixture
def memory_repo():
    """Repositorio en memoria limpio por prueba."""
    repo = InMemoryRoutesRepositoryAdapter()
    repo.reset()
    return repo