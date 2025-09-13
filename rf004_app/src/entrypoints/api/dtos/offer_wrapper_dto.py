from pydantic import BaseModel
from src.entrypoints.api.dtos.created_offer_dto import CreatedOfferInfoDto

class OfferWrapperDto(BaseModel):
    """Offer domain model."""
    data: CreatedOfferInfoDto = None
    msg: str = "Oferta creada exitosamente"
