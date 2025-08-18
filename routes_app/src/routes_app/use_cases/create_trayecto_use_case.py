from routes_app.domain.models.models import Trayecto
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.domain.use_cases.base_use_case import BaseUseCase

class CreateTrayectoUseCase(BaseUseCase):
    """
    Caso de uso para crear un trayecto.
    """
    def __init__(self, repository: RoutesRepositoryPort):
        self.repository = repository

    def execute(self, trayecto: Trayecto) -> Trayecto:
        return self.repository.create(trayecto)