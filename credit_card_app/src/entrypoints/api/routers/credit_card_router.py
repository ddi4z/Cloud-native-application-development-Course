from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import List, Dict
from pydantic import BaseModel, ValidationError
from uuid import UUID 

from src.assembly import (
    build_create_credit_card_use_case,
    build_get_credit_cards_by_user_use_case,
    build_get_credit_cards_count_use_case,
    build_reset_credit_cards_use_case,
    build_update_credit_card_status_use_case, 
)
from src.domain.models.credit_card import CreditCard, CreditCardStatus #
from src.domain.models.credit_card_creation_request import CreditCardCreationRequest
from src.entrypoints.api.auth_handler import get_current_user_data
from src.errors import (
    MalformedRequestError,
    CardAlreadyExistsError,
    CardExpiredError,
    ServiceCommunicationError
)

from src.entrypoints.api.schemas.credit_card_schemas import (
    CreditCardCreatedResponse, CreditCardPublic
)

router = APIRouter(prefix="/credit-cards")

class StatusUpdateRequest(BaseModel):
    """Modelo para el cuerpo de la petición de actualización de estado."""
    status: CreditCardStatus # Valida que el valor sea uno de los del Enum ("APROBADA" o "RECHAZADA")

@router.post(
    "/",
    response_model=CreditCardCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Tarjeta creada con éxito."},
        400: {"description": "Campos inválidos, vacíos o con formato incorrecto."},
        401: {"description": "El token no es válido o está vencido."},
        403: {"description": "No hay token en la solicitud."},
        409: {"description": "El usuario ya había almacenado la misma tarjeta."},
        412: {"description": "La tarjeta de crédito ya está vencida."},
    }
)
def create_credit_card(
    request: CreditCardCreationRequest,
    user_data: Dict = Depends(get_current_user_data),
    use_case = Depends(build_create_credit_card_use_case),
):
    """Crea una tarjeta asociada al usuario al que pertenece el token."""
    try:
        card = use_case.execute(user_data["user_id"], request, user_data["user_email"])
        return {
            "id": str(card.id),
            "userId": card.userId,
            "createdAt": card.createdAt.isoformat(),
        }
    except MalformedRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except CardAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except CardExpiredError as e:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=e.message)
    except ServiceCommunicationError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[CreditCardPublic])
def get_user_cards(
    user_data: Dict = Depends(get_current_user_data),
    use_case = Depends(build_get_credit_cards_by_user_use_case),
):
    cards = use_case.execute(user_data["user_id"])
    return [
        CreditCardPublic(
            id=str(c.id),
            token=str(c.token),
            userId=str(c.userId),
            lastFourDigits=str(c.lastFourDigits),
            issuer=c.issuer,
            status=c.status,
            createdAt=c.createdAt,
            updatedAt=c.updatedAt,
        )
        for c in cards
    ]

@router.patch(
    "/internal/cards/{card_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Actualiza el estado de una tarjeta (Uso interno por el poller)",
    include_in_schema=False # Oculta este endpoint de la documentación pública
)
def update_card_status_by_poller(
    card_id: UUID,
    request: StatusUpdateRequest,
    use_case = Depends(build_update_credit_card_status_use_case),
):
    """
    Endpoint interno para que el worker de polling actualice el estado
    de una tarjeta después de la verificación.
    """
    try:
        updated_card = use_case.execute(card_id=str(card_id), status=request.status)
        if not updated_card:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarjeta no encontrada.")
        return {"msg": f"Estado de la tarjeta {card_id} actualizado exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno al actualizar la tarjeta: {e}")

@router.get("/count")
def get_cards_count(use_case = Depends(build_get_credit_cards_count_use_case)):
    """Usado para consultar cuantas entidades de tarjetas están en la base de datos."""
    count = use_case.execute()
    return {"count": count}

@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Usado para verificar el estado del servicio."""
    return "pong"

@router.post("/reset")
def reset_database(use_case = Depends(build_reset_credit_cards_use_case)):
    """Usado para eliminar todas las tarjetas."""
    use_case.execute()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"msg": "Todos los datos fueron eliminados"}
    )