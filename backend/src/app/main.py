from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes.ws import router as ws_router
from app.core.db import SessionLocal
from app.core.logging import configure_logging
from app.core.settings import settings
from app.services.admin_auth import ensure_admin_user


@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as session:
        ensure_admin_user(
            session,
            username=settings.admin_username,
            password=settings.admin_password,
            display_name=settings.admin_display_name,
        )
        session.commit()
    yield


configure_logging()
app = FastAPI(
    title="校园通知服务 API",
    description="校园通知系统的后端服务接口文档。支持微信小程序登录、设备管理、设备绑定、通知推送及 WebSocket 实时通信。",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(ws_router)


@app.get("/health", summary="健康检查", description="返回服务运行状态")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
