from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import List, Dict
from pydantic import ValidationError

from src.assembly import (
    build_create_credit_card_use_case,
    build_get_credit_cards_by_user_use_case,
    build_get_credit_cards_count_use_case,
    build_reset_credit_cards_use_case,
)
from src.domain.models.credit_card import CreditCard
from src.domain.models.credit_card_creation_request import CreditCardCreationRequest
from src.entrypoints.api.auth_handler import get_current_user_data
from src.errors import (
    MalformedRequestError,
    CardAlreadyExistsError, 
    CardExpiredError, 
    ServiceCommunicationError
)

router = APIRouter(prefix="/credit-cards")

@router.post(
    "/",
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
        # Pasamos los datos del usuario directamente al caso de uso
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

# --- 2. Ver tarjetas ---
@router.get("/", response_model=List[CreditCard])
def get_user_cards(
    user_data: Dict = Depends(get_current_user_data),
    use_case = Depends(build_get_credit_cards_by_user_use_case),
):
    """Retorna el listado de tarjetas de crédito que pertenecen al usuario."""
    return use_case.execute(user_data["user_id"])

# --- 3. Consultar cantidad de entidades ---
@router.get("/count")
def get_cards_count(use_case = Depends(build_get_credit_cards_count_use_case)):
    """Usado para consultar cuantas entidades de tarjetas están en la base de datos."""
    count = use_case.execute()
    return {"count": count}

# --- 4. Consulta de salud del servicio ---
@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Usado para verificar el estado del servicio."""
    return "pong"

# --- 5. Restablecer base de datos ---
@router.post("/reset")
def reset_database(use_case = Depends(build_reset_credit_cards_use_case)):
    """Usado para eliminar todas las tarjetas."""
    use_case.execute()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"msg": "Todos los datos fueron eliminados"}
    )