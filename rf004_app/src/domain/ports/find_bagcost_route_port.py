from abc import abstractmethod

from typing import Optional

from .http_request import HttpRequest


class FindBagCostRoutePort(HttpRequest):
    """Offer repository interface."""

    @abstractmethod
    def get_bagcost(self, routeId: str) -> Optional[int]:
        """Create a new offer."""
        raise NotImplementedError("This method should be overridden in subclasses")
