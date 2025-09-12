from src.domain.ports.create_offer_port import CreateOfferPort

from typing import Optional

from src.domain.models.offer import Offer, CreatedOffer

import requests


class CreateOfferAdapter(CreateOfferPort):
    """"""

    def __init__(self, service_url: str):
        self.service_url = service_url

    def create_offer(
        self, offer: Offer, userId: str, postId: str
    ) -> Optional[CreatedOffer]:
        request_body = {"userId": userId, "postId": postId} | offer.model_dump()

        response = requests.post(
            f"{self.service_url}",
            json=request_body,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 201:
            return None

        return CreatedOffer(**response.json())
