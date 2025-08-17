from fastapi import FastAPI
from routes_app.entrypoints.api.routers.routes import router as routes_router

app = FastAPI(title="Routes App", version="1.0.0")

app.include_router(routes_router, prefix="/routes")

@app.get("/")
def root():
    return {"service": "routes_app", "status": "ok"}