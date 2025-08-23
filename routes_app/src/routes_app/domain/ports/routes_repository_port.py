from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from routes_app.domain.models.models import Trayecto


class RoutesRepositoryPort(ABC):
    """
    Puerto que define el contrato para las operaciones de persistencia
    de la entidad Trayecto.
    """

    @abstractmethod
    def create(self, trayecto: Trayecto) -> Trayecto:
        """Crea una instancia de Trayecto y lo retorna"""
        raise NotImplementedError

    @abstractmethod
    def get(self, trayecto_id: UUID) -> Optional[Trayecto]:
        """Obtiene un trayecto por su ID. Retorna None si no existe."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, trayecto_id: UUID) -> bool:
        """Elimina un trayecto por ID. Retorna True si existía y se eliminó."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[Trayecto]:
        """Retorna una lista con todos los trayectos existentes."""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Elimina todos los datos del repositorio (usado para tests)."""
        raise NotImplementedError

    @abstractmethod
    def get_by_flight_id(self, flight_id: str) -> Optional[Trayecto]:
        """Busca un trayecto por su flightId. Retorna None si no se encuentra."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Retorna la cantidad total de trayectos en el repositorio."""
        raise NotImplementedError
