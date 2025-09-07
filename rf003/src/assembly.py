# src/assembly.py
import os
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.entrypoints.api.routers.post_router_rf003 import router as publications_router
from src.entrypoints.api.routers.post_router_rf003 import get_uc as get_uc_placeholder
from src.domain.use_cases.create_post import CreatePublicationUseCase
from src.adapters.http_users.fake_users import FakeUsers  # swap to HttpUsers later
from src.adapters.http_routes.fake_routes import FakeRoutes
from src.adapters.http_posts.fake_posts import FakePosts
from src.adapters.uniques_repo_sqlite.uniques_repo_sqlite import SqliteUniques
from src.errors import UnauthorizedError, ValidationError, ConflictError, DependencyError

# ---- minimal clock ----
class SystemClock:
    def now(self):
        return datetime.now(timezone.utc)

# ---- build the real use case (FAKE adapters for local) ----
def build_uc() -> CreatePublicationUseCase:
    users = FakeUsers()
    routes = FakeRoutes()
    posts = FakePosts()
    uniques = SqliteUniques(os.getenv("UNIQUES_URL", "sqlite:///./uniques.db"))
    clock = SystemClock()
    return CreatePublicationUseCase(users, routes, posts, uniques, clock)

# ---- FastAPI app ----
app = FastAPI(title="RF003 publication_api", version="0.1.0")

# provide the dependency implementation for the placeholder in the router
app.dependency_overrides[get_uc_placeholder] = build_uc

# include endpoints
app.include_router(publications_router)

# healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}

# nice error mapping
@app.exception_handler(UnauthorizedError)
async def _unauth(_: Request, exc: UnauthorizedError):
    return JSONResponse({"detail": str(exc)}, status_code=401)

@app.exception_handler(ValidationError)
async def _val(_: Request, exc: ValidationError):
    return JSONResponse({"detail": str(exc)}, status_code=400)

@app.exception_handler(ConflictError)
async def _conf(_: Request, exc: ConflictError):
    return JSONResponse({"detail": str(exc)}, status_code=409)

@app.exception_handler(DependencyError)
async def _dep(_: Request, exc: DependencyError):
    return JSONResponse({"detail": str(exc)}, status_code=502)