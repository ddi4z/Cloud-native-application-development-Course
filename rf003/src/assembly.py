# src/assembly.py
import os
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.entrypoints.api.routers.router import router as rf003_router
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.create_post import CreatePostUseCase
from src.adapters.http_users.fake_users import FakeUsers  # swap to HttpUsers later
from src.adapters.http_routes.fake_routes import FakeRoutes
from src.adapters.http_posts.fake_posts import FakePosts
from src.adapters.uniques_repo_sqlite.uniques_repo_sqlite import SqliteUniques
from src.errors import ValidationError, ConflictError

# ---- minimal clock ----
class SystemClock:
    def now(self):
        return datetime.now(timezone.utc)



def create_post_use_case() -> BaseUseCase:
    pass

