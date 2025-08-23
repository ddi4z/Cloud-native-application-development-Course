from routes_app.domain.models.models import Trayecto
from routes_app.domain.use_cases.count_trayectos_use_case import CountTrayectosUseCase
from uuid import uuid4


def test_count_returns_number_of_items(memory_repo, trayecto):
    uc = CountTrayectosUseCase(repository=memory_repo)
    assert uc.execute() == 0
    memory_repo.create(trayecto)
    trayecto_2 = Trayecto(
        **{**trayecto.model_dump(), "id": uuid4(), "flightId": "FL456"}
    )
    memory_repo.create(trayecto_2)

    assert uc.execute() == 2
