from __future__ import annotations
from typing import Protocol, Optional
from datetime import datetime

from src.domain.models.route_input import RouteInput
from src.domain.models.publication_request import PublicationRequest

class UsersPort(Protocol):
    def get_current_user(self, token: str) -> str: ...  # returns user_id

class RoutesPort(Protocol):
    def find_by_fingerprint(self, fp: str) -> Optional[str]: ...
    def create(self, route: RouteInput) -> str: ...

class PostsPort(Protocol):
    def user_has_post_for_route(self, user_id: str, route_id: str) -> bool: ...
    def create(self, user_id: str, route_id: str, req: PublicationRequest) -> str: ...

class UniquesPort(Protocol):
    # atomic guard: True if inserted, False if already exists
    def try_claim(self, user_id: str, route_fp: str) -> bool: ...
    def release(self, user_id: str, route_fp: str) -> None: ...

class Clock(Protocol):
    def now(self) -> datetime: ...