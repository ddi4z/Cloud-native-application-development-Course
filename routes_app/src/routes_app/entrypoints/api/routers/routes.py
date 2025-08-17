from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["routes"])

@router.get("/ping", response_class=PlainTextResponse)
def ping() -> str:
    return "pong"

@router.post("/reset")
def reset():
    # Mock por ahora
    return {"msg": "Todos los datos fueron eliminados"}