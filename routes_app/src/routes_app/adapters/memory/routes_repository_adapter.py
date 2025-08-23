from typing import Dict, List, Optional
from uuid import UUID
from routes_app.domain.models.models import Trayecto
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort


class InMemoryRoutesRepositoryAdapter(RoutesRepositoryPort):
    """
    Implementación en memoria del puerto del repositorio de trayectos.
    """

    def __init__(self) -> None:
        """Inicializa el repositorio en memoria."""
        self._items: Dict[UUID, Trayecto] = {}

    def create(self, trayecto: Trayecto) -> Trayecto:
        """
        Añade un nuevo trayecto al repositorio.
        Args:
            trayecto (Trayecto): El objeto Trayecto que se va a almacenar.
        Returns:
            Trayecto: El trayecto guardado.
        """
        self._items[trayecto.id] = trayecto
        return trayecto

    def update(self, trayecto: Trayecto) -> Trayecto:
        """
        Actualiza un trayecto existente en el repositorio.
        Args:
            trayecto (Trayecto): El objeto Trayecto con los datos actualizados.
        Returns:
            Trayecto: El trayecto actualizado.
        """
        self._items[trayecto.id] = trayecto
        return trayecto

    def get(self, trayecto_id: UUID) -> Optional[Trayecto]:
        """
        Busca un trayecto por su ID.
        Args:
            trayecto_id tipo  UUID: El ID del trayecto a buscar.
        Returns:
            Optional [Trayecto]: El objeto Trayecto si se encuentra, de lo contrario None.
        """
        return self._items.get(trayecto_id)

    def delete(self, trayecto_id: UUID) -> bool:
        """
        Elimina un trayecto del repositorio por su ID.
        Args:
            trayecto_id en UUID: El ID del trayecto a eliminar.
        Returns:
            bool: True si el trayecto existía y fue eliminado, False en caso contrario.
        """
        return self._items.pop(trayecto_id, None) is not None

    def list(self) -> List[Trayecto]:
        """
        Retorna una lista de todos los trayectos en el repositorio.
        Returns:
            List[Trayecto]: Una lista con todos los objetos Trayecto.
        """
        return list(self._items.values())

    def reset(self) -> None:
        """Elimina todos los trayectos."""
        self._items.clear()

    def get_by_flight_id(self, flight_id: str) -> Optional[Trayecto]:
        """
        Busca un trayecto por su flight_id.
        Args:
            flight_id (str): El flightId único del trayecto a buscar.
        Returns:
            Optional[Trayecto]: El objeto Trayecto si se encuentra, de lo contrario None.
        """
        for t in self._items.values():
            if t.flightId == flight_id:
                return t
        return None

    def count(self) -> int:
        """
        Retorna el número total de trayectos almacenados.
        Returns:
            int: La cantidad de trayectos.
        """
        return len(self._items)
