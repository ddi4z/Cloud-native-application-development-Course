import pytest
from datetime import datetime, timedelta, timezone
from src.routes_app.domain.models.models import Trayecto

def test_trayecto_valido(trayecto):
    assert trayecto.flightId == "FL123"
    assert trayecto.sourceAirportCode == "BOG"
    assert trayecto.destinyAirportCode == "MDE"
    assert trayecto.plannedEndDate > trayecto.plannedStartDate

def test_airport_codes_deben_ser_3_letras_y_upper(valid_trayecto_data):
    data = valid_trayecto_data.copy()
    data["sourceAirportCode"] = "bo1"  # inválido
    with pytest.raises(ValueError):
        Trayecto(**data)

def test_inicio_no_puede_ser_pasado(valid_trayecto_data):
    data = valid_trayecto_data.copy()
    data["plannedStartDate"] = datetime.now(timezone.utc) - timedelta(days=1)
    with pytest.raises(ValueError):
        Trayecto(**data)

def test_end_debe_ser_posterior(valid_trayecto_data):
    data = valid_trayecto_data.copy()
    data["plannedEndDate"] = data["plannedStartDate"]  # igual → inválido
    with pytest.raises(ValueError):
        Trayecto(**data)