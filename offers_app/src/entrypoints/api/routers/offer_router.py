from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

from src.assembly import (
    build_create_offer_use_case,
    build_delete_offer_use_case,
    build_get_offer_use_case,
    build_get_offers_use_case,
    build_count_offers_use_case,
    build_reset_offers_use_case,
)
from src.domain.models.offer import Offer
from src.domain.use_cases.base_use_case import BaseUseCase
from typing import Optional
from fastapi import Query
from src.errors import (
    OfferNotFoundError,
    PreconditionOfferFailedError,
    InvalidFieldInOfferError,
)
from src.entrypoints.api.dtos.created_offer_dto import CreatedOfferDto

router = APIRouter(prefix="/offers")


@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"


@router.get("/count", status_code=200)
def count_offers(use_case: BaseUseCase = Depends(build_count_offers_use_case)):
    """Count the number of offers."""
    return JSONResponse({"count": use_case.execute()})


@router.post("/reset", status_code=200)
def reset_offers(use_case: BaseUseCase = Depends(build_reset_offers_use_case)):
    """Reset the offers repository."""
    use_case.execute()
    return JSONResponse({"msg": "Offers repository reset successfully."})


@router.post("/", response_model=CreatedOfferDto, status_code=201)
def create_offer(
    offer: Offer, use_case: BaseUseCase = Depends(build_create_offer_use_case)
):
    """Create a new offer."""
    try:
        # FastAPI will automatically convert the Offer model
        # to the CreatedOfferDto model
        return use_case.execute(offer)
    except Exception as e:
        status_code = None
        if isinstance(e, PreconditionOfferFailedError):
            status_code = 412
        elif isinstance(e, InvalidFieldInOfferError):
            status_code = 400
        return HTTPException(status_code=status_code, detail=str(e))


@router.get("/{offer_id}", response_model=Offer, status_code=200)
def get_offer(offer_id: str, use_case: BaseUseCase = Depends(build_get_offer_use_case)):
    """Get a offer by ID."""
    try:
        offer = use_case.execute(offer_id)
    except InvalidFieldInOfferError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OfferNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return offer


# TODO: Do this thing :(
@router.get("/", response_model=List[Offer])
def get_offers(
    post: Optional[str] = Query(None, description="ID of the post"),
    owner: Optional[str] = Query(None, description="ID of the post"),
    use_case: BaseUseCase = Depends(build_get_offers_use_case),
):
    """Get all offers."""
    return use_case.execute()


@router.delete("/{offer_id}", response_model=Offer)
def delete_offer(
    offer_id: str, use_case: BaseUseCase = Depends(build_delete_offer_use_case)
):
    """Delete offer."""
    try:
        use_case.execute(offer_id)
        return JSONResponse({"msg": "la oferta fue eliminada"}, status_code=200)
    except OfferNotFoundError as _:
        raise HTTPException(status_code=404, detail="Offer not found")
    except InvalidFieldInOfferError as _:
        raise HTTPException(status_code=400, detail="Invalid offer ID")
