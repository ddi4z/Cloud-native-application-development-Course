from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.entrypoints.api.routers.credit_card_router import router as cc_router

app = FastAPI(
    title="Servicio de Tarjetas de Crédito",
    version="1.0.0",
    description="Microservicio para la gestión y verificación de tarjetas de crédito."
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Solicitud inválida"})

app.include_router(cc_router)

@app.get("/")
def read_root():
    return {"status": "Servicio de Tarjetas de Crédito está activo"}

