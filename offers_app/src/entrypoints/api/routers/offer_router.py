from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

from src.assembly import (
    build_create_offer_use_case,
    build_delete_offer_use_case,
    build_get_offer_use_case,
    build_get_offers_use_case,
    build_update_offer_use_case,
)
from src.domain.models.offer import Offer
from src.domain.use_cases.base_use_case import BaseUseCase
from src.errors import OfferNotFoundError, PreconditionOfferFailedError, InvalidFieldInOfferError

router = APIRouter(prefix="/offers")


@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"


@router.post("/", response_model=Offer, status_code=201)
def create_offer(offer: Offer, use_case: BaseUseCase = Depends(build_create_offer_use_case)):
    """Create a new offer."""
    try:
        return use_case.execute(offer)
    except InvalidFieldInOfferError as e:
        return JSONResponse(
            {"error": str(e)}, status_code=400
        )
    except PreconditionOfferFailedError as e:
        return JSONResponse(
            {"error": str(e)}, status_code=412
        )

@router.get("/{offer_id}", response_model=Offer)
def get_offer(offer_id: int, use_case: BaseUseCase = Depends(build_get_offer_use_case)):
    """Get a offer by ID."""
    offer = use_case.execute(offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="offer not found")
    return offer


@router.get("/", response_model=List[Offer])
def get_offers(use_case: BaseUseCase = Depends(build_get_offers_use_case)):
    """Get all offers."""
    return use_case.execute()


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


@router.delete("/{offer_id}", response_model=Offer)
def delete_offer(offer_id: int, use_case: BaseUseCase = Depends(build_delete_offer_use_case)):
    """Delete offer."""
    try:
        return use_case.execute(offer_id)
    except OfferNotFoundError as err:
        return JSONResponse({"error": str(err)}, status_code=404)
