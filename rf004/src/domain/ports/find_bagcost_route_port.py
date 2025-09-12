from abc import abstractmethod

from src.domain.ports.http_request_port import HttpRequestPort

from typing import Optional

class FindBagCostRoutePort(HttpRequestPort):
    """Offer repository interface."""

    @abstractmethod
    def get_bagcost(self, routeId: str) -> Optional[int]:
        """Create a new offer."""
        raise NotImplementedError("This method should be overridden in subclasses")
