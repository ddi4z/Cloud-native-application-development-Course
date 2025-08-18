from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, ValidationError 
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Importamos los Casos de Uso
from routes_app.domain.use_cases.base_use_case import BaseUseCase
from routes_app.assembly import (
    build_create_trayecto_use_case,
    build_get_trayecto_use_case,
    build_list_trayectos_use_case,
    build_delete_trayecto_use_case,
    build_get_trayecto_by_flight_id_use_case,
    build_count_trayectos_use_case,
    build_reset_trayectos_use_case,
)
from routes_app.domain.models.models import Trayecto

router = APIRouter(tags=["Trayectos"])

@router.get("/ping", response_class=PlainTextResponse)
def ping() -> str:
    """Endpoint de salud para verificar que el servicio está activo."""
    return "pong"

@router.post("/reset", status_code=200)
def reset(use_case: BaseUseCase = Depends(build_reset_trayectos_use_case)):
    """Elimina todos los datos del repositorio."""
    use_case.execute()
    return {"msg": "Todos los datos fueron eliminados"}

# DTOs (Data Transfer Objects)
class TrayectoIn(BaseModel):
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    destinyCountry: str
    bagCost: int = Field(ge=0)
    plannedStartDate: datetime
    plannedEndDate: datetime

class TrayectoOut(BaseModel):
    id: UUID
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    destinyCountry: str
    bagCost: int
    plannedStartDate: datetime
    plannedEndDate: datetime
    createdAt: datetime
    updatedAt: datetime

# Endpoints CRUD usando Casos de Uso
@router.post("/", response_model=TrayectoOut, status_code=201)
def create_trayecto(
    payload: TrayectoIn,
    use_case: BaseUseCase = Depends(build_create_trayecto_use_case),
    get_by_flight_id_uc: BaseUseCase = Depends(build_get_trayecto_by_flight_id_use_case)
):
    """Crea un nuevo trayecto."""
    if get_by_flight_id_uc.execute(payload.flightId):
        raise HTTPException(status_code=409, detail="flightId ya existe")

    try:
        trayecto_a_crear = Trayecto(**payload.model_dump())
        nuevo_trayecto = use_case.execute(trayecto_a_crear)
        return TrayectoOut.model_validate(nuevo_trayecto.model_dump())
    except ValidationError:
        raise JSONResponse(
            status_code=412,
            content={"msg": "Las fechas del trayecto no son válidas"},
        )

@router.get("/", response_model=List[TrayectoOut])
def list_trayectos(
    flightId: Optional[str] = Query(default=None),
    list_uc: BaseUseCase = Depends(build_list_trayectos_use_case),
    get_by_flight_id_uc: BaseUseCase = Depends(build_get_trayecto_by_flight_id_use_case)
):
    """Lista todos los trayectos o filtra por flightId."""
    if flightId:
        trayecto = get_by_flight_id_uc.execute(flightId)
        return [TrayectoOut.model_validate(trayecto.model_dump())] if trayecto else []
    
    items = list_uc.execute()
    return [TrayectoOut.model_validate(t.model_dump()) for t in items]

@router.get("/{trayecto_id}", response_model=TrayectoOut)
def get_trayecto(
    trayecto_id: UUID,
    use_case: BaseUseCase = Depends(build_get_trayecto_use_case)
):
    """Obtiene un trayecto por su ID."""
    trayecto = use_case.execute(trayecto_id)
    if not trayecto:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado")
    return TrayectoOut.model_validate(trayecto.model_dump())

@router.delete("/{trayecto_id}", status_code=204)
def delete_trayecto(
    trayecto_id: UUID,
    use_case: BaseUseCase = Depends(build_delete_trayecto_use_case)
):
    """Elimina un trayecto por su ID."""
    if not use_case.execute(trayecto_id):
        raise HTTPException(status_code=404, detail="Trayecto no encontrado")

@router.get("/count", response_model=dict)
def count_trayectos(use_case: BaseUseCase = Depends(build_count_trayectos_use_case)):
    """Cuenta el número total de trayectos."""
    return {"count": use_case.execute()}