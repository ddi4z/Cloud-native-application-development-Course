import httpx
from typing import Optional
from src.domain.ports.rf003_port import RoutesPort
from src.domain.models.route_input import RouteInput

class HttpRoutes(RoutesPort):
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
    def find_by_fingerprint(self, fp: str) -> Optional[str]:
        r = httpx.get(f"{self.base}/routes?fp={fp}", timeout=5)
        if r.status_code == 404: return None
        r.raise_for_status()
        return r.json()["id"]
    def create(self, route: RouteInput) -> str:
        r = httpx.post(f"{self.base}/routes", json=route.model_dump(), timeout=5)
        r.raise_for_status()
        return r.json()["id"]