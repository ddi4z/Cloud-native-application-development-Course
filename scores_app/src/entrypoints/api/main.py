from fastapi import FastAPI

from src.entrypoints.api.routers.score_router import router as score_router
from src.config import Settings


app = FastAPI(title=Settings.app_name)
app.include_router(score_router)
