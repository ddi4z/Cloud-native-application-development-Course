from typing import Optional

from routes_app.domain.models.models import Trayecto
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.domain.use_cases.base_use_case import BaseUseCase


class GetTrayectoByFlightIdUseCase(BaseUseCase):
    """
    Caso de uso para buscar un trayecto por su flightId.
    """

    def __init__(self, repository: RoutesRepositoryPort):
        self.repository = repository

    def execute(self, flight_id: str) -> Optional[Trayecto]:
        return self.repository.get_by_flight_id(flight_id)
