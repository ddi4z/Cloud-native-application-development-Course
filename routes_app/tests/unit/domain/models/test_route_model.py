from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from routes_app.domain.models.models import Trayecto


@pytest.fixture
def valid_trayecto_data():
    """Genera datos para un trayecto válido."""
    now = datetime.now(timezone.utc)
    return {
        "flightId": "AV123",
        "sourceAirportCode": "BOG",
        "sourceCountry": "Colombia",
        "destinyAirportCode": "MIA",
        "destinyCountry": "USA",
        "bagCost": 50,
        "plannedStartDate": now + timedelta(days=1),
        "plannedEndDate": now + timedelta(days=2),
    }


@pytest.fixture
def trayecto(valid_trayecto_data):
    """Instancia válida de Trayecto a partir del fixture de datos."""
    return Trayecto(**valid_trayecto_data)


# Tests
def test_trayecto_valido(trayecto):
    assert trayecto.flightId == "AV123"
    assert trayecto.sourceAirportCode == "BOG"
    assert trayecto.destinyAirportCode == "MIA"
    assert trayecto.plannedEndDate > trayecto.plannedStartDate


def test_create_trayecto_success(valid_trayecto_data):
    """
    Prueba la creación exitosa de un objeto Trayecto.
    """
    t = Trayecto(**valid_trayecto_data)
    assert t.flightId == valid_trayecto_data["flightId"]
    # Debe estar en mayúsculas
    assert t.sourceAirportCode == "BOG"
    assert t.bagCost == 50
    assert isinstance(t.id, type(uuid4()))
    assert isinstance(t.createdAt, datetime)
    assert isinstance(t.updatedAt, datetime)


def test_airport_code_validator(valid_trayecto_data):
    """
    Prueba que el validador de código de aeropuerto funcione correctamente. Falla si el formato es incorrecto
    """
    # Caso exitoso con minúsculas
    data = valid_trayecto_data.copy()
    data["sourceAirportCode"] = "bog"
    t = Trayecto(**data)
    assert t.sourceAirportCode == "BOG"

    # Caso fallido con números
    data = valid_trayecto_data.copy()
    data["destinyAirportCode"] = "M1A"
    with pytest.raises(ValidationError):
        Trayecto(**data)

    # Caso fallido con longitud incorrecta
    data = valid_trayecto_data.copy()
    data["destinyAirportCode"] = "MIAMI"
    with pytest.raises(ValidationError):
        Trayecto(**data)


def test_start_date_in_past_fails(valid_trayecto_data):
    """
    Prueba que la creación de un trayecto falle si la fecha de inicio está en el pasado.
    """
    data = valid_trayecto_data.copy()
    data["plannedStartDate"] = datetime.now(timezone.utc) - timedelta(days=1)
    with pytest.raises(ValidationError) as excinfo:
        Trayecto(**data)
    assert "La fecha de inicio no puede estar en el pasado" in str(excinfo.value)


def test_end_date_before_start_date_fails(valid_trayecto_data):
    """
    Prueba que la creación de un trayecto falle si la fecha de fin es anterior a la de inicio.
    """
    data = valid_trayecto_data.copy()
    data["plannedEndDate"] = data["plannedStartDate"] - timedelta(hours=1)
    with pytest.raises(ValidationError) as excinfo:
        Trayecto(**data)
    assert "La fecha de fin debe ser posterior a la fecha de inicio" in str(
        excinfo.value
    )
