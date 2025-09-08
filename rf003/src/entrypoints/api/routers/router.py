from fastapi import APIRouter, Depends, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import Annotated

from src.domain.models.models import PostCreationRequest
from src.domain.models.models import PublicationResponse

from src.domain.use_cases.base_use_case import BaseUseCase

from src.errors import (
    ValidationError,
    InvalidTokenError,
    NoTokenError,
    InvalidRouteDatesError,
    InvalidExpiredAtError,
    ConflictError,
    ServiceCommunicationError,
)


router = APIRouter(prefix='/rf003')


@router.get(
        '/posts',
        response_model=PublicationResponse,
        responses={
            201: {'description': "Operación exitosa"},
            400: {'description': "Información incompleta o errónea"},
            401: {'description': "Token inválido o vencido"},
            403: {'description': "Token no está en la solicitud"},
            412: {'description': "Las fechas del trayecto no son válidas"},
            412: {'description': "La fecha expiración no es válida"},
            412: {'description': "El usuario ya tiene una publicación para la misma fecha"},
            503: {'description': "El servicio está temporalmente fuera de servicio"},
        }
)

async def create_post(
    #variables
    post_creation_dto: PostCreationRequest,
    # Autorización
    authorization: Annotated[str | None, Header()] = None,
    # use case a ejecutar
    use_case: BaseUseCase = Depends(create_post_use_case), # depende del assembly
):
    """
    Endpoint para crear una publicación.
    Recibe post_creation_dto
    Ejecuta use case CreatePost
    """

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="El token no está en la solicitud.")

    token = authorization.split("Bearer ")[1]
    
    try:
        result = await use_case.execute(post_creation_dto)
        return result
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    except NoTokenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    except InvalidRouteDatesError as e:
        raise JSONResponse(status_code=412, content={"msg":"Las fechas del trayecto no son válidas"})
    
    except InvalidExpiredAtError as e:
        raise JSONResponse(status_code=412, content={"msg":"La fecha expiración no es válida"})
    
    except ConflictError as e:
        raise JSONResponse(status_code=412, content={"msg":"El usuario ya tiene una publicación para la misma fecha"})
    
    except ServiceCommunicationError:
        return JSONResponse(status_code=503, content={"msg":"El servicio está temporalmente fuera de servicio."})
    
    except Exception:
        return JSONResponse(status_code=503, content={"msg":"El servicio está temporalmente fuera de servicio."})
    

@router.get("/ping", status_code=200, tags=["Health Check"])
def health_check():
    """
    Verifica que el servicio esté activo y responde un 'pong'.
    """
    return {"status": "pong"}
