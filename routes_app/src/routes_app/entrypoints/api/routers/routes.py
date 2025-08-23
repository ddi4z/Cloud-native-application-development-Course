from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field, ValidationError

from routes_app.assembly import (
    build_count_trayectos_use_case,
    build_create_trayecto_use_case,
    build_delete_trayecto_use_case,
    build_get_trayecto_by_flight_id_use_case,
    build_get_trayecto_use_case,
    build_list_trayectos_use_case,
    build_reset_trayectos_use_case,
)
from routes_app.domain.models.models import Trayecto
from routes_app.domain.use_cases.base_use_case import BaseUseCase

# Importamos la excepción para poder manejarla
from routes_app.errors import TrayectoNotFoundError

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
    get_by_flight_id_uc: BaseUseCase = Depends(
        build_get_trayecto_by_flight_id_use_case
    ),
):
    """Crea un nuevo trayecto."""
    try:
        # Si get_by_flight_id encuentra algo, significa que el flightId ya existe.
        get_by_flight_id_uc.execute(payload.flightId)
        return JSONResponse(status_code=412, content={"msg": "flightId ya existe"})
    except TrayectoNotFoundError:
        try:
            trayecto_a_crear = Trayecto(**payload.model_dump())
            nuevo_trayecto = use_case.execute(trayecto_a_crear)
            return TrayectoOut.model_validate(nuevo_trayecto.model_dump())
        except ValidationError:
            return JSONResponse(
                status_code=412,
                content={"msg": "Las fechas del trayecto no son válidas"},
            )


@router.get("/count", response_model=dict)
def count_trayectos(use_case: BaseUseCase = Depends(build_count_trayectos_use_case)):
    """Cuenta el número total de trayectos."""
    return {"count": use_case.execute()}


@router.get("/", response_model=List[TrayectoOut])
def list_trayectos(
    flightId: Optional[str] = Query(default=None, alias="flight"),
    list_uc: BaseUseCase = Depends(build_list_trayectos_use_case),
    get_by_flight_id_uc: BaseUseCase = Depends(
        build_get_trayecto_by_flight_id_use_case
    ),
):
    """Lista todos los trayectos o filtra por flightId."""
    if flightId:
        try:
            trayecto = get_by_flight_id_uc.execute(flightId)
            return [TrayectoOut.model_validate(trayecto.model_dump())]
        except TrayectoNotFoundError:
            return []
    items = list_uc.execute()
    return [TrayectoOut.model_validate(t.model_dump()) for t in items]


@router.get("/{trayecto_id}", response_model=TrayectoOut)
def get_trayecto(
    trayecto_id: UUID, use_case: BaseUseCase = Depends(build_get_trayecto_use_case)
):
    """Obtiene un trayecto por su ID."""
    try:
        trayecto = use_case.execute(trayecto_id)
        return TrayectoOut.model_validate(trayecto.model_dump())
    except TrayectoNotFoundError:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado")


@router.delete("/{trayecto_id}", status_code=200)
def delete_trayecto(
    trayecto_id: UUID, use_case: BaseUseCase = Depends(build_delete_trayecto_use_case)
):
    """Elimina un trayecto por su ID."""
    try:
        use_case.execute(trayecto_id)
        return {"msg": "el trayecto fue eliminado"}
    except TrayectoNotFoundError:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado")
