from typing import Optional
from uuid import UUID
from routes_app.domain.models.models import Trayecto
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.domain.use_cases.base_use_case import BaseUseCase

class GetTrayectoUseCase(BaseUseCase):
    """
    Caso de uso para obtener un trayecto por su ID.
    """
    def __init__(self, repository: RoutesRepositoryPort):
        self.repository = repository

    def execute(self, trayecto_id: UUID) -> Optional[Trayecto]:
        return self.repository.get(trayecto_id)