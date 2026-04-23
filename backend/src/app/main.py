from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes.ws import router as ws_router
from app.log_config import configure_logging
from app.settings import settings

configure_logging()
app = FastAPI(
    title="校园通知服务 API",
    description="校园通知系统的后端服务接口文档。支持微信小程序登录、设备管理、设备绑定、通知推送及 WebSocket 实时通信。",
    version="1.0.0",
    debug=settings.debug,
)
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)


@app.get("/health", summary="健康检查", description="返回服务运行状态")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
