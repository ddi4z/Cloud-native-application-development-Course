import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Annotated

from src.assembly import build_create_post_use_case

from src.domain.use_cases.base_use_case import BaseUseCase


from src.domain.models.models import CreatePost, UserInput, PublicationResponse, PublicationResponseData, RouteDetails
#CreatePost, PublicationResponse


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

security = HTTPBearer()

def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    return credentials.credentials


@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """
    Verifica que el servicio esté activo y responde un 'pong'.
    """
    return "pong"




@router.post(
    "/posts", response_model=PublicationResponse, status_code=201
)

async def create_post(
    input_dto: UserInput,
    token: str = Depends(get_current_token), 
    create_post_use_case: BaseUseCase = Depends(build_create_post_use_case),
):
    """Crea una nueva publicación."""
    if not token:
        raise HTTPException(status_code=403, detail="Token is required")
    
    try:
        created_post, expire_at, route_id, route_created_at = await create_post_use_case.execute(token=token, input_dto=input_dto)

        route_details = RouteDetails(
            id = route_id,
            createdAt= route_created_at
        )

        publication_response_data = PublicationResponseData(
            id = created_post.id,
            userId=created_post.userId,
            createdAt=created_post.createdAt,
            expireAt=expire_at,
            route=route_details
        )

        api_answer = PublicationResponse(
            data=publication_response_data
        )
        return api_answer
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    except NoTokenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    except InvalidRouteDatesError as e:
        return JSONResponse(
            status_code=412,
            content={"msg": "Las fechas del trayecto no son válidas"},
        )
    
    except InvalidExpiredAtError as e:
        return JSONResponse(
            status_code=412,
            content={"msg": "La fecha expiración no es válida"},
        )
    
    except ConflictError as e:
        return JSONResponse(
            status_code=412,
            content={"msg": "El usuario ya tiene una publicación para la misma fecha"},
        )
    
    except ServiceCommunicationError as e:
        return JSONResponse(
            status_code=503,
            content={"msg": "El servicio está temporalmente fuera de servicio."},
        )
    
    except Exception:
        logging.exception("Ocurrió un error fatal no controlado en RF003")
        return JSONResponse(
            status_code=503,
            content={"msg": "El servicio está temporalmente fuera de servicio."},
        )
    




"""


@router.post(
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
    post_creation_dto: CreatePost,
    # Autorización
    authorization: Annotated[str | None, Header()] = None,
    # use case a ejecutar
    use_case: BaseUseCase = Depends(build_create_post_use_case),
):
    
    #Endpoint para crear una publicación.
    #Recibe post_creation_dto
    #Ejecuta use case CreatePost
    

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
    


"""