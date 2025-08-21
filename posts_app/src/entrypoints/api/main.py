from fastapi import FastAPI

from src.config import Settings
from src.entrypoints.api.routers.post_router import router as post_router

app = FastAPI(title=Settings.app_name)
app.include_router(post_router)


# Add custom exception handler here
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.errors(),
            "body": exc.body
        },
    )