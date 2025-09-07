from fastapi import APIRouter, Depends, Header
from src.domain.models.publication_request import PublicationRequest
from src.domain.models.auth_context import AuthContext
from src.domain.models.publication_result import PublicationResult
from src.domain.use_cases.create_post import CreatePublicationUseCase


router = APIRouter()

def get_auth(authorization: str = Header(default=None)) -> AuthContext:
    token = ""
    if authorization and "Bearer " in authorization:
        token = authorization.split("Bearer ", 1)[1]
    return AuthContext(user_id="unknown", token=token)

# Placeholder; assembly.py will inject the real implementation
def get_uc() -> CreatePublicationUseCase:
    raise RuntimeError("CreatePublicationUseCase provider not wired yet")

@router.post("/publications", response_model=PublicationResult, status_code=201)
def create_publication(
    req: PublicationRequest,
    auth: AuthContext = Depends(get_auth),
    uc: CreatePublicationUseCase = Depends(get_uc),
):
    return uc.execute(auth, req)