from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from routes_app.entrypoints.api.main import app

client = TestClient(app)


def test_ping_endpoint():
    """Prueba que el endpoint de salud /ping funcione correctamente."""
    response = client.get("/routes/ping")
    assert response.status_code == 200
    assert response.text == "pong"


def test_create_and_get_trayecto():
    """
    Prueba de integración para crear un trayecto y luego obtenerlo.
    Esto cubre el código en routes.py, main.py y assembly.py.
    """
    client.post("/routes/reset")

    # Datos para crear un nuevo trayecto
    start_date = datetime.now(timezone.utc) + timedelta(days=1)
    end_date = start_date + timedelta(days=1)

    trayecto_data = {
        "flightId": "INT-TEST-01",
        "sourceAirportCode": "BOG",
        "sourceCountry": "Colombia",
        "destinyAirportCode": "MIA",
        "destinyCountry": "USA",
        "bagCost": 100,
        "plannedStartDate": start_date.isoformat(),
        "plannedEndDate": end_date.isoformat(),
    }

    response_create = client.post("/routes/", json=trayecto_data)

    assert response_create.status_code == 201
    created_data = response_create.json()
    assert created_data["flightId"] == "INT-TEST-01"
    assert "id" in created_data

    trayecto_id = created_data["id"]

    response_get = client.get(f"/routes/{trayecto_id}")

    assert response_get.status_code == 200
    get_data = response_get.json()
    assert get_data["id"] == trayecto_id
    assert get_data["flightId"] == "INT-TEST-01"

    response_count = client.get("/routes/count")
    assert response_count.status_code == 200
    assert response_count.json()["count"] == 1


def test_create_trayecto_with_invalid_start_date():
    """
    Traducción de la prueba de Postman: "Creación de trayecto plannedStartDate invalido".
    Verifica que la API devuelva un error 412 si la fecha de inicio está en el pasado.
    """
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    future_date = datetime.now(timezone.utc) + timedelta(days=1)

    invalid_trayecto_data = {
        "flightId": "INT-TEST-INVALID-DATE",
        "sourceAirportCode": "BOG",
        "sourceCountry": "Colombia",
        "destinyAirportCode": "MIA",
        "destinyCountry": "USA",
        "bagCost": 100,
        "plannedStartDate": past_date.isoformat(),
        "plannedEndDate": future_date.isoformat(),
    }

    response = client.post("/routes/", json=invalid_trayecto_data)

    assert response.status_code == 412
    response_data = response.json()
    assert response_data["msg"] == "Las fechas del trayecto no son válidas"
