from .catch_unavailable_service import catch_unavailable_service

from src.domain.ports.find_bagcost_route_port import FindBagCostRoutePort
from src.domain.models.route_bagcost import RouteBagCost

from typing import Optional

import requests
from requests.models import Response

class FindBagCostRouteAdapter(FindBagCostRoutePort):
    """"""

    def __init__(self, service_url: str):
        self.service_url = service_url

    @catch_unavailable_service("Route")
    def get_bagcost(self, routeId: str) -> Optional[int]:
        response: Response = requests.post(f"{self.service_url}/routes/{routeId}")
        if response.status_code != 200:
            return None

        return RouteBagCost(**response.json()).bagCost
