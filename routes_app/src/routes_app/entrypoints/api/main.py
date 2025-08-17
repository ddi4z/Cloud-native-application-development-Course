from fastapi import FastAPI

app = FastAPI(title="Routes App", version="1.0.0")

@app.get("/")
def root():
    return {"service": "routes_app", "status": "ok"}