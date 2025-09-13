from fastapi import FastAPI

from config import Settings
from src.entrypoints.api.routers.offer_router import router as offer_router

app = FastAPI(title=Settings.app_name)
app.include_router(offer_router)
