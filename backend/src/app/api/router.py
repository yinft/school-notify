from fastapi import APIRouter

from app.api.routes import auth, binding, device, notification, user
from app.api.routes import admin_auth, admin_dashboard, admin_devices, admin_notifications, admin_users, admin_versions, public_versions


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin_auth.router, prefix="/admin/auth", tags=["admin-auth"])
api_router.include_router(admin_dashboard.router, prefix="/admin/dashboard", tags=["admin-dashboard"])
api_router.include_router(admin_devices.router, prefix="/admin/devices", tags=["admin-devices"])
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin-users"])
api_router.include_router(admin_notifications.router, prefix="/admin/notifications", tags=["admin-notifications"])
api_router.include_router(admin_versions.router, prefix="/admin/versions", tags=["admin-versions"])
api_router.include_router(public_versions.router, prefix="/public/versions", tags=["public-versions"])
api_router.include_router(device.router, tags=["devices"])
api_router.include_router(binding.router, tags=["bindings"])
api_router.include_router(notification.router, tags=["notifications"])
api_router.include_router(user.router, tags=["users"])
