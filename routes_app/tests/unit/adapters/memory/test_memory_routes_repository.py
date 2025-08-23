from typing import Dict, List, Optional
from uuid import UUID

from routes_app.domain.models.models import Trayecto
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort
from routes_app.errors import FlightIdAlreadyExistsError, TrayectoNotFoundError


class InMemoryRoutesRepositoryAdapter(RoutesRepositoryPort):
    """
    Implementación en memoria del puerto del repositorio de trayectos.
    """

    def __init__(self) -> None:
        """Inicializa el repositorio en memoria."""
        self._items: Dict[UUID, Trayecto] = {}

    def create(self, trayecto: Trayecto) -> Trayecto:
        """
        Añade un nuevo trayecto al repositorio, lanzando un error si el flightId ya existe.
        """
        # --- LÓGICA AÑADIDA ---
        # Verificamos si ya existe un trayecto con el mismo flightId
        for existing_trayecto in self._items.values():
            if existing_trayecto.flightId == trayecto.flightId:
                raise FlightIdAlreadyExistsError(
                    f"El flightId '{trayecto.flightId}' ya existe."
                )
        # --- FIN DE LA LÓGICA AÑADIDA ---

        self._items[trayecto.id] = trayecto
        return trayecto

    def update(self, trayecto: Trayecto) -> Trayecto:
        """Actualiza un trayecto existente en el repositorio."""
        self._items[trayecto.id] = trayecto
        return trayecto

    def get(self, trayecto_id: UUID) -> Trayecto:
        """
        Busca un trayecto por su ID. Lanza TrayectoNotFoundError si no lo encuentra.
        """
        # --- LÓGICA MODIFICADA ---
        trayecto = self._items.get(trayecto_id)
        if not trayecto:
            raise TrayectoNotFoundError(
                f"Trayecto con id '{trayecto_id}' no encontrado."
            )
        return trayecto
        # --- FIN DE LA LÓGICA MODIFICADA ---

    def delete(self, trayecto_id: UUID) -> bool:
        """Elimina un trayecto del repositorio por su ID."""
        return self._items.pop(trayecto_id, None) is not None

    def list(self) -> List[Trayecto]:
        """Retorna una lista de todos los trayectos en el repositorio."""
        return list(self._items.values())

    def reset(self) -> None:
        """Elimina todos los trayectos."""
        self._items.clear()

    def get_by_flight_id(self, flight_id: str) -> Optional[Trayecto]:
        """Busca un trayecto por su flight_id."""
        for t in self._items.values():
            if t.flightId == flight_id:
                return t
        return None

    def count(self) -> int:
        """Retorna el número total de trayectos almacenados."""
        return len(self._items)
