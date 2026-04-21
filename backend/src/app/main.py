from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes.ws import router as ws_router
from app.settings import settings


app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
