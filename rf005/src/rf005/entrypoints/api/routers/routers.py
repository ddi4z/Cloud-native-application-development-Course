from fastapi import APIRouter, Depends, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import Annotated

from ....assembly import build_get_full_publication_use_case
from ....domain.use_cases.get_post_sorted_by_score_use_case import GetPostSortedByScoreUseCase
from ....domain.models import PublicationResponse
from ....errors import AuthorizationError, ServiceCommunicationError, EntityNotFoundError, InvalidTokenError

router = APIRouter(prefix="/rf005")

@router.get("/ping")
def ping():
    """Endpoint para verificar que el servicio está activo."""
    return Response(content="pong", status_code=200)

@router.get(
    "/posts/{post_id}",
    response_model=PublicationResponse,
    responses={
        200: {"description": "Operación exitosa"},
        401: {"description": "El token no es válido o está vencido."},
        403: {"description": "El usuario no tiene permiso para ver el contenido."},
        404: {"description": "La publicación no existe."},
        503: {"description": "El servicio está temporalmente fuera de servicio."},
    }
)
async def get_publication_details(
    post_id: str,
    authorization: Annotated[str | None, Header()] = None,
    use_case: GetPostSortedByScoreUseCase = Depends(build_get_full_publication_use_case),
):
    """
    Endpoint para obtener los detalles completos de una publicación,
    incluyendo sus ofertas ordenadas por utilidad (score).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="El token no está en la solicitud.")

    token = authorization.split("Bearer ")[1]

    try:
        result = await use_case.execute(post_id, token)
        return result
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ServiceCommunicationError:
        return JSONResponse(
            status_code=503,
            content={"msg": "El servicio está temporalmente fuera de servicio."}
        )
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"msg": "El servicio está temporalmente fuera de servicio."}
        )