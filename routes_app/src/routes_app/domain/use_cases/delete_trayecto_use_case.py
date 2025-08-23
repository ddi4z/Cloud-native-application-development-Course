from uuid import UUID
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.domain.use_cases.base_use_case import BaseUseCase

class DeleteTrayectoUseCase(BaseUseCase):
    """
    Caso de uso para eliminar un trayecto.
    """
    def __init__(self, repository: RoutesRepositoryPort):
        self.repository = repository

    def execute(self, trayecto_id: UUID) -> bool:
        return self.repository.delete(trayecto_id)