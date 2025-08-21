from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routes_app.entrypoints.api.routers.routes import router as routes_router

app = FastAPI(title="Routes App", version="1.0.0")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Este manejador captura los errores de campos faltantes o con formato incorrecto
    y devuelve un código 400 Bad Request.
    """
    return JSONResponse(
        status_code=400,
        content={"detail": "Error de validación: campos requeridos faltantes o con formato incorrecto"},
    )


app.include_router(routes_router, prefix="/routes")

@app.get("/")
def root():
    return {"service": "routes_app", "status": "ok"}

