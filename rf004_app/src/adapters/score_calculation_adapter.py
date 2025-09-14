from src.domain.ports.score_calculation_port import ScoreCalculationPort

from typing import Optional
from src.domain.models.score import Score
from requests.models import Response

import requests

from .catch_unavailable_service import catch_unavailable_service

from src.errors import UnavailableService

class ScoreCalculationAdapter(ScoreCalculationPort):
    """"""

    def __init__(self, service_url: str):
        self.service_url = service_url

    @catch_unavailable_service("Score")
    def calculate_score(self, score: Score) -> Optional[int]:
        response: Response = requests.post(
            self.service_url,
            json=score.model_dump(),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 201:  # created
            return None

        return response.json().get("score")

    @catch_unavailable_service("Score")
    def ping(self) -> None:
        response: Response = requests.get(f"{self.service_url}/ping")
        if response.status_code != 200:
            raise UnavailableService("Score service is not working")
