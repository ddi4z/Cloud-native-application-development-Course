from routes_app.domain.use_cases.get_trayecto_by_flight_id_use_case import (
    GetTrayectoByFlightIdUseCase,
)


def test_get_by_flight_id_ok(memory_repo, trayecto):
    trayecto.flightId = "FL-123"
    memory_repo.create(trayecto)
    uc = GetTrayectoByFlightIdUseCase(repository=memory_repo)
    got = uc.execute("FL-123")

    assert got is not None
    assert got.flightId == "FL-123"


def test_get_by_flight_id_not_found(memory_repo):
    uc = GetTrayectoByFlightIdUseCase(repository=memory_repo)
    assert uc.execute("NO-EXISTS") is None
