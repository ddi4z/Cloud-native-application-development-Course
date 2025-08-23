import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from routes_app.domain.models.models import Trayecto
from routes_app.adapters.memory.routes_repository_adapter import InMemoryRoutesRepositoryAdapter

@pytest.fixture
def future_window():
    """
    Devuelve un par de fechas (inicio, fin) en el futuro,
    con 24 horas de diferencia entre ellas.
    """
    start = datetime.now(timezone.utc) + timedelta(hours=24)
    end = start + timedelta(hours=24)
    return start, end

@pytest.fixture
def valid_trayecto_data(future_window):
    """
    Genera un diccionario con datos válidos para crear un Trayecto.
    Utiliza la fixture 'future_window' para las fechas.
    """
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
    """
    Crea una instancia válida y lista para usar del modelo Trayecto.
    Depende de la fixture 'valid_trayecto_data'.
    """
    return Trayecto(**valid_trayecto_data)

@pytest.fixture
def memory_repo():
    """
    Proporciona una instancia limpia del repositorio en memoria para cada prueba.
    Asegura que las pruebas estén aisladas entre sí.
    """
    repo = InMemoryRoutesRepositoryAdapter()
    repo.reset()  # Se asegura de que esté vacío antes de cada uso
    return repo
