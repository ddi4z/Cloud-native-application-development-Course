import hashlib
from src.domain.models.route_input import RouteInput

def route_fingerprint(r: RouteInput) -> str:
    key = f"{r.origin.strip().lower()}|{r.destination.strip().lower()}|{r.departure_at.isoformat()}"
    return hashlib.sha256(key.encode()).hexdigest()