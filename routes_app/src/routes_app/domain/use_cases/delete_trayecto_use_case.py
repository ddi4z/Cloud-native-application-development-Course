import logging
from uuid import UUID

from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.domain.use_cases.base_use_case import BaseUseCase
from routes_app.errors import InfrastructureError

logger = logging.getLogger(__name__)


class DeleteTrayectoUseCase(BaseUseCase):
    """
    Caso de uso para eliminar un trayecto.
    """

    def __init__(self, repository: RoutesRepositoryPort):
        self.repository = repository

    def execute(self, trayecto_id: UUID) -> bool:
        try:
            return self.repository.delete(trayecto_id)
        except Exception as e:
            logger.error(f"Error inesperado al eliminar trayecto {trayecto_id}: {e}")

            # Opcional: relanzar un error más genérico
            raise InfrastructureError("Error inesperado en la capa de datos.")
