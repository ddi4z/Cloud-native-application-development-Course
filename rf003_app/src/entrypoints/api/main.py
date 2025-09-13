from fastapi import FastAPI
from src.entrypoints.api.routers.router import router as rf003_router

app = FastAPI(
    title='Orquestador RF-003',
    version='1.0.0',
    description="MS orquestador para crear posts"
    )


app.include_router(rf003_router)


@app.get("/")
def read_root():
    """Endpoint raíz que confirma que el servicio está en funcionamiento."""
    return {"status": "Servicio de orquestación RF-003 está activo"}