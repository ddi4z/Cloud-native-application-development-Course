from typing import List, Union

from fastapi import APIRouter, Depends, Response
from fastapi.responses import PlainTextResponse

from src.domain.models.score_request import ScoreRequest
from src.assembly import (
    build_calculate_score_use_case,
)
from src.domain.use_cases.base_use_case import BaseUseCase
from src.errors import (
    InvalidSizeError
)

router = APIRouter(prefix="/scores")



@router.post("/", status_code=201)
def calculate_score(
    score_request: Union[ScoreRequest, List[ScoreRequest]],
    use_case: BaseUseCase = Depends(build_calculate_score_use_case),
):
    requests = score_request if isinstance(score_request, list) else [score_request]

    results = []
    for req in requests:
        try:
            calculated_score = use_case.execute(req)
            results.append({
                "offer_id": req.offer_id,
                "score": calculated_score
            })
        except InvalidSizeError:
            return Response(status_code=400)
    results.sort(key=lambda x: -x["score"])
    return results[0] if isinstance(score_request, ScoreRequest) else results

@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"