from fastapi import FastAPI
from src.config import Settings
from src.entrypoints.api.routers.router import router as rf003_router

app = FastAPI(title=Settings.app_name)
app.include_router(rf003_router)