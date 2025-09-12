from src.domain.ports.score_calculation_port import ScoreCalculationPort

from typing import Optional
from src.domain.models.score import Score
from src.domain.models.post import Post

import requests

class ScoreCalculationAdapter(ScoreCalculationPort):
    """"""

    def __init__(self, service_url: str):
        self.service_url = service_url

    def calculate_score(self, postId: str, offerSize: str) -> Optional[Score]:
        return 1000
