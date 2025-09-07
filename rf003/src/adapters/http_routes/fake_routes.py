from typing import Optional
from src.domain.ports.rf003_port import RoutesPort
from src.domain.models.route_input import RouteInput

class FakeRoutes(RoutesPort):
    def __init__(self): self.store = {}  # fp -> route_id
    def find_by_fingerprint(self, fp: str) -> Optional[str]:
        return self.store.get(fp)
    def create(self, route: RouteInput) -> str:
        rid = f"route-{len(self.store)+1}"
        # store by fingerprint in tests; real adapter will call API
        return rid