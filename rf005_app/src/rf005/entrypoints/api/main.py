from fastapi import FastAPI
from .routers.routers import router as rf005_router

# Creación de la app FastAPI
# Se crea una instancia principal de la app.
app = FastAPI(
    title="Orquestador RF-005",
    version="1.0.0",
    description="Microservicio orquestador para consultar publicaciones con ofertas ordenadas por score."
)

# Inclusión de Routers
# Se registra el router que contiene todos los endpoints definidos para RF-005
app.include_router(rf005_router)

# Endpoint Raíz para una verificación de salud básica
@app.get("/")
def read_root():
    """Endpoint raíz que confirma que el servicio está en funcionamiento."""
    return {"status": "Servicio de orquestación RF-005 está activo"}