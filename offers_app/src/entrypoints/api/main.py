from fastapi import FastAPI

from config import Settings
from src.entrypoints.api.routers.offer_router import router as offer_router
from src.adapters.postgres.db_config import init_db

app = FastAPI(title=Settings.app_name)
app.include_router(offer_router)

@app.on_event("startup")
async def startup_event():
    init_db()
