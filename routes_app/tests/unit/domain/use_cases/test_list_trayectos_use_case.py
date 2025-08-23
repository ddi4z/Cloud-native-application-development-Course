from uuid import uuid4

from routes_app.domain.models.models import Trayecto
from routes_app.domain.use_cases.list_trayectos_use_case import ListTrayectosUseCase


def test_list_returns_all(memory_repo, trayecto):
    uc = ListTrayectosUseCase(repository=memory_repo)

    # Creamos el primer trayecto con un flightId específico
    trayecto.flightId = "F1"
    memory_repo.create(trayecto)

    # Creamos un segundo trayecto diferente
    trayecto_2 = Trayecto(**{**trayecto.model_dump(), "id": uuid4(), "flightId": "F2"})
    memory_repo.create(trayecto_2)

    result = uc.execute()
    assert len(result) == 2
