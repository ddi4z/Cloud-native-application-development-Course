from fastapi import FastAPI
from src.config import Settings
from src.entrypoints.api.routers.router import router as rf003_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title=Settings.app_name)
app.include_router(rf003_router)


@app.exception_handler(RequestValidationError)
async def _map_422_to_400(_, __):
    return JSONResponse(status_code=400, content={"msg": "Bad request"})