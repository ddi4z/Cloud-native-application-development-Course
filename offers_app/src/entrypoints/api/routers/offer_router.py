from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

from src.assembly import (
    build_create_offer_use_case,
    build_delete_offer_use_case,
    build_get_offer_use_case,
    build_get_offers_use_case,
    build_update_offer_use_case,
    build_count_offers_use_case,
    build_reset_offers_use_case,
)
from src.domain.models.offer import Offer
from src.domain.use_cases.base_use_case import BaseUseCase
from typing import Optional
from fastapi import Query
from src.errors import OfferNotFoundError, PreconditionOfferFailedError, InvalidFieldInOfferError

router = APIRouter(prefix="/offers")


@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"

@router.get("/count", status_code=200)
def count_offers(use_case: BaseUseCase = Depends(build_count_offers_use_case)):
    """Count the number of offers."""
    try:
        return JSONResponse({'count': use_case.execute()})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@router.post("/reset", status_code=200)
def reset_offers(use_case: BaseUseCase = Depends(build_reset_offers_use_case)):
    """Reset the offers repository."""
    try:
        use_case.execute()
        return JSONResponse({"message": "Offers repository reset successfully."})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@router.post("/", response_model=Offer, status_code=201)
def create_offer(offer: Offer, use_case: BaseUseCase = Depends(build_create_offer_use_case)):
    """Create a new offer."""
    try:
        return use_case.execute(offer)
    except Exception as e:
        status_code = 400
        if isinstance(e, PreconditionOfferFailedError):
            status_code = 412
        elif isinstance(e, InvalidFieldInOfferError):
            pass
        return JSONResponse(
            {"error": str(e)}, status_code=status_code
        )

@router.get("/{offer_id}", response_model=Offer, status_code=200)
def get_offer(offer_id: str, use_case: BaseUseCase = Depends(build_get_offer_use_case)):
    """Get a offer by ID."""
    try:
        offer = use_case.execute(offer_id)
    except InvalidFieldInOfferError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    print(offer)
    if not offer:
        raise HTTPException(status_code=404, detail="offer not found")
    return offer


# TODO
@router.get("/", response_model=List[Offer])
def get_offers(
    post: Optional[str] = Query(None, description="ID of the post"),
    owner: Optional[str] = Query(None, description="ID of the post"),  
    use_case: BaseUseCase = Depends(build_get_offers_use_case)
):
    """Get all offers."""
    return use_case.execute()


# TODO
@router.put("/{offer_id}", response_model=Offer)
def update_offer(
    offer_id: int, offer: Offer, use_case: BaseUseCase = Depends(build_update_offer_use_case)
):
    """Update offer."""
    try:
        offer.id = offer_id
        return use_case.execute(offer)
    except OfferNotFoundError as err:
        return JSONResponse({"error": str(err)}, status_code=404)


# TODO
@router.delete("/{offer_id}", response_model=Offer)
def delete_offer(offer_id: int, use_case: BaseUseCase = Depends(build_delete_offer_use_case)):
    """Delete offer."""
    try:
        return use_case.execute(offer_id)
    except OfferNotFoundError as err:
        return JSONResponse({"error": str(err)}, status_code=404)
