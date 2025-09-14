from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from src.errors import (
    UnauthorizedError,
    PostNotFoundError,
    OfferOnOwnPostError,
    InvalidOfferInputError,
    PostExpiredError,
    UnavailableService,
)

from src.assembly import build_create_offer_use_case

from src.domain.use_cases.base_use_case import BaseUseCase
from src.entrypoints.api.dtos.created_offer_dto import CreatedOfferInfoDto

from src.entrypoints.api.dtos.offer_info_dto import OfferInfoDto
from src.entrypoints.api.dtos.offer_wrapper_dto import OfferWrapperDto

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from src.domain.models.offer import CreatedOffer

import uuid

router = APIRouter(prefix="/rf004")


security = HTTPBearer()


def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    return credentials.credentials


@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"


# use a path param called postId
# obtain the headers of the request
@router.post("/posts/{postId}/offers", response_model=OfferWrapperDto, status_code=201)
def create_offer(
    offer: OfferInfoDto,
    postId: str,
    create_offer_use_case: BaseUseCase = Depends(build_create_offer_use_case),
    token: str = Depends(get_current_token),
):
    """Create a new offer."""
    if token == "":
        raise HTTPException(status_code=403, detail="Token is required")

    try:
        # validate if postId is a valid UUID
        uuid.UUID(postId)

        # call users to obtain the user model
        # if the token is not valid, it will raise an exception
        # otherwise, it will return the user model
        created_offer: CreatedOffer = create_offer_use_case.execute(
            auth_token=token,
            post_id=postId,
            offer=offer,
        )

        created_offer_dto: CreatedOfferInfoDto = CreatedOfferInfoDto.from_domain(
            created_offer, postId=postId
        )

        return OfferWrapperDto(data=created_offer_dto)

    # input should to have all the required fields
    except InvalidOfferInputError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # 401: invalid token
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))
    # post not found
    except PostNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # user tries to create an offer on their own post
    except OfferOnOwnPostError as e:
        raise HTTPException(status_code=412, detail=str(e))
    # post has expired
    except PostExpiredError as e:
        raise HTTPException(status_code=412, detail=str(e))
    # if the postId or token is not a valid UUID
    except ValueError as _:
        raise HTTPException(status_code=400, detail="Remember that IDs are UUIDs")
    # if there's some service down, response with
    # the response code should to be {"msg": "El servicio está temporalmente fuera de servicio."}
    except UnavailableService as _:
        return JSONResponse(
            status_code=503,
            content={"msg": "El servicio está temporalmente fuera de servicio."},
        )
