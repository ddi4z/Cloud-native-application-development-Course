from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.domain.use_cases.base_use_case import BaseUseCase


class CountTrayectosUseCase(BaseUseCase):
    """
    Caso de uso para contar el total de trayectos.
    """

    def __init__(self, repository: RoutesRepositoryPort):
        self.repository = repository

    def execute(self) -> int:
        return self.repository.count()
