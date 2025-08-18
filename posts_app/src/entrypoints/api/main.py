from fastapi import FastAPI

from src.config import Settings
from src.entrypoints.api.routers.post_router import router as post_router

app = FastAPI(title=Settings.app_name)
app.include_router(post_router)


from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body  # Optional: for debugging
        }
    )