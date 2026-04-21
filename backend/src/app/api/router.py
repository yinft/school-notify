from fastapi import APIRouter

from app.api.routes import auth, binding, device, notification, user


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(device.router, tags=["devices"])
api_router.include_router(binding.router, tags=["bindings"])
api_router.include_router(notification.router, tags=["notifications"])
api_router.include_router(user.router, tags=["users"])
