from typing import Dict, List, Optional
from uuid import UUID
from routes_app.domain.models.models import Trayecto
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort


class InMemoryRouteRepository(RoutesRepositoryPort):
    def __init__(self) -> None:
        self._items: Dict[UUID, Trayecto] = {}

    def create(self, trayecto: Trayecto) -> Trayecto:
        self._items[trayecto.id] = trayecto
        return trayecto

    def update(self, trayecto: Trayecto) -> Trayecto:
        self._items[trayecto.id] = trayecto
        return trayecto

    def get(self, trayecto_id: UUID) -> Optional[Trayecto]:
        return self._items.get(trayecto_id)

    def delete(self, trayecto_id: UUID) -> bool:
        return self._items.pop(trayecto_id, None) is not None

    def list(self) -> List[Trayecto]:
        return list(self._items.values())

    def reset(self) -> None:
        self._items.clear()