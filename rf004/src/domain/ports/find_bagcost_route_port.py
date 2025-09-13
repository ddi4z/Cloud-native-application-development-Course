from abc import abstractmethod, ABC

from typing import Optional

class FindBagCostRoutePort(ABC):
    """Offer repository interface."""

    @abstractmethod
    def get_bagcost(self, routeId: str) -> Optional[int]:
        """Create a new offer."""
        raise NotImplementedError("This method should be overridden in subclasses")
