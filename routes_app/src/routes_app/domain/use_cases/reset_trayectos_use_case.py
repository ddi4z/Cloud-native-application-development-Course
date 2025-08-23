from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.domain.use_cases.base_use_case import BaseUseCase


class ResetTrayectosUseCase(BaseUseCase):
    """
    Caso de uso para eliminar todos los trayectos.
    """

    def __init__(self, repository: RoutesRepositoryPort):
        self.repository = repository

    def execute(self) -> None:
        """
        Delega el reinicio al repositorio.
        """
        return self.repository.reset()
