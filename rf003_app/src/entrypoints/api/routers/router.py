from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from src.assembly import build_create_post_use_case
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.models.models import (
    UserInput,
    PublicationResponse,
    PublicationResponseData,
    RouteDetails,
)
from src.errors import (
    ValidationError,
    InvalidTokenError,
    NoTokenError,
    InvalidRouteDatesError,
    InvalidExpiredAtError,
    ConflictError,
    ServiceCommunicationError,
)

router = APIRouter(prefix="/rf003")
logger = logging.getLogger(__name__)


@router.get("/ping")
async def ping():
    return {"msg": "RF003 up"}


def _extract_bearer_token(authorization_header: Optional[str]) -> str:
    if not authorization_header:
        raise NoTokenError("Token no está en la solicitud")
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise NoTokenError("Formato de autorización inválido. Usa: Bearer <token>")
    return parts[1]


@router.post("/posts", response_model=PublicationResponse, status_code=201)
async def create_post(input_dto: UserInput, Authorization: Optional[str] = Header(None)):
    case: BaseUseCase = build_create_post_use_case()

    # Extraer token
    try:
        token = _extract_bearer_token(Authorization)
    except NoTokenError as e:
        # Los tests esperan 403 cuando no hay token
        raise HTTPException(status_code=403, detail=str(e))

    try:
        created_post, expire_at, route_id, route_created_at = await case.execute(
            token=token, input_dto=input_dto
        )

        # Éxito
        response = PublicationResponse(
            msg="Publicación creada con éxito",
            data=PublicationResponseData(
                id=created_post.id,
                userId=created_post.userId,
                createdAt=created_post.createdAt,
                route=RouteDetails(
                    id=route_id,
                    flightId=input_dto.flightId,
                    createdAt=route_created_at,
                ),
            ),
        )
        return response

    except InvalidRouteDatesError:
        # plannedStartDate / plannedEndDate inválidos
        return JSONResponse(
            status_code=412,
            content={"msg": "Las fechas del trayecto no son válidas"},
        )

    except InvalidExpiredAtError:
        # expireAt inválido
        return JSONResponse(
            status_code=412,
            content={"msg": "La fecha expiración no es válida"},
        )

    except ConflictError:
        # Usuario ya tiene una publicación para la misma fecha/trayecto
        return JSONResponse(
            status_code=412,
            content={"msg": "El usuario ya tiene una publicación para la misma fecha"},
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ServiceCommunicationError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        logger.error("Ocurrió un error fatal no controlado en RF003", exc_info=True)
        raise HTTPException(status_code=503, detail="Error interno en RF003")
