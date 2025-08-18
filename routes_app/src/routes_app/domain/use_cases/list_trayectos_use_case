from typing import List
from routes_app.domain.models.models import Trayecto
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.domain.use_cases.base_use_case import BaseUseCase

class ListTrayectosUseCase(BaseUseCase):
    """
    Caso de uso para listar todos los trayectos.
    """
    def __init__(self, repository: RoutesRepositoryPort):
        self.repository = repository

    def execute(self) -> List[Trayecto]:
        return self.repository.list()