from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Device, Notification, NotificationDelivery, User, UserDevice


def list_admin_devices(db: Session, *, keyword: str | None = None, status: str | None = None) -> list[dict[str, object]]:
    devices = db.execute(select(Device).order_by(Device.id.asc())).scalars().all()
    results: list[dict[str, object]] = []
    for device in devices:
        if status and device.status != status:
            continue
        if keyword and keyword not in device.device_id and keyword not in device.device_name and keyword not in device.location_label:
            continue
        bound_users_count = len(db.execute(select(UserDevice).where(UserDevice.device_id == device.device_id)).scalars().all())
        results.append(
            {
                "device_id": device.device_id,
                "device_name": device.device_name,
                "location_label": device.location_label,
                "client_version": device.client_version,
                "status": device.status,
                "bound_users_count": bound_users_count,
            }
        )
    return results


def paginate_items(items: list[dict[str, object]], *, page: int, page_size: int) -> tuple[list[dict[str, object]], int]:
    normalized_page = max(page, 1)
    normalized_page_size = max(page_size, 1)
    start = (normalized_page - 1) * normalized_page_size
    end = start + normalized_page_size
    return items[start:end], len(items)


def get_admin_device_detail(db: Session, *, device_id: str) -> dict[str, object] | None:
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        return None
    bindings = db.execute(select(UserDevice).where(UserDevice.device_id == device_id)).scalars().all()
    bound_users = []
    for binding in bindings:
        user = db.execute(select(User).where(User.user_id == binding.user_id)).scalar_one_or_none()
        bound_users.append({"user_id": binding.user_id, "nickname": user.nickname if user else None})
    deliveries = db.execute(select(NotificationDelivery).where(NotificationDelivery.device_id == device_id)).scalars().all()
    recent_notifications = []
    for delivery in deliveries:
        notification = db.execute(select(Notification).where(Notification.notification_id == delivery.notification_id)).scalar_one_or_none()
        if notification:
            recent_notifications.append(
                {
                    "notification_id": notification.notification_id,
                    "title": notification.title,
                    "sender_user_id": notification.sender_user_id,
                }
            )
    return {
        "device_id": device.device_id,
        "device_name": device.device_name,
        "location_label": device.location_label,
        "client_version": device.client_version,
        "status": device.status,
        "bound_users": bound_users,
        "recent_notifications": recent_notifications,
    }


def update_admin_device(db: Session, *, device_id: str, device_name: str | None, location_label: str | None) -> Device | None:
    device = db.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
    if device is None:
        return None
    if device_name is not None:
        device.device_name = device_name
    if location_label is not None:
        device.location_label = location_label
    db.flush()
    return device


def unbind_admin_device_user(db: Session, *, device_id: str, user_id: str) -> bool:
    binding = db.execute(select(UserDevice).where(UserDevice.device_id == device_id, UserDevice.user_id == user_id)).scalar_one_or_none()
    if binding is None:
        return False
    db.delete(binding)
    db.flush()
    return True


def list_admin_users(db: Session, *, keyword: str | None = None) -> list[dict[str, object]]:
    users = db.execute(select(User).order_by(User.id.asc())).scalars().all()
    items: list[dict[str, object]] = []
    for user in users:
        nickname = user.nickname or ""
        if keyword and keyword not in user.user_id and keyword not in nickname:
            continue
        count = len(db.execute(select(UserDevice).where(UserDevice.user_id == user.user_id)).scalars().all())
        items.append(
            {
                "user_id": user.user_id,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "bound_devices_count": count,
            }
        )
    return items


def get_admin_user_detail(db: Session, *, user_id: str) -> dict[str, object] | None:
    user = db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()
    if user is None:
        return None
    bindings = db.execute(select(UserDevice).where(UserDevice.user_id == user_id)).scalars().all()
    devices = []
    for binding in bindings:
        device = db.execute(select(Device).where(Device.device_id == binding.device_id)).scalar_one_or_none()
        if device:
            devices.append(
                {
                    "device_id": device.device_id,
                    "device_name": device.device_name,
                    "location_label": device.location_label,
                    "client_version": device.client_version,
                    "status": device.status,
                }
            )
    notifications = db.execute(select(Notification).where(Notification.sender_user_id == user_id)).scalars().all()
    recent_notifications = [
        {"notification_id": item.notification_id, "title": item.title, "created_at": item.created_at.isoformat()} for item in notifications
    ]
    return {
        "user_id": user.user_id,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "devices": devices,
        "recent_notifications": recent_notifications,
    }


def list_admin_notifications(db: Session, *, keyword: str | None = None, sender_user_id: str | None = None) -> list[dict[str, object]]:
    notifications = db.execute(select(Notification).order_by(Notification.id.desc())).scalars().all()
    items: list[dict[str, object]] = []
    for item in notifications:
        if sender_user_id and item.sender_user_id != sender_user_id:
            continue
        if keyword and keyword not in item.title and keyword not in item.content:
            continue
        deliveries = db.execute(select(NotificationDelivery).where(NotificationDelivery.notification_id == item.notification_id)).scalars().all()
        success_count = sum(1 for delivery in deliveries if delivery.received and not delivery.failed)
        failed_count = sum(1 for delivery in deliveries if delivery.failed)
        items.append(
            {
                "notification_id": item.notification_id,
                "sender_user_id": item.sender_user_id,
                "title": item.title,
                "created_at": item.created_at.isoformat(),
                "success_count": success_count,
                "failed_count": failed_count,
            }
        )
    return items


def get_admin_notification_detail(db: Session, *, notification_id: str) -> dict[str, object] | None:
    notification = db.execute(select(Notification).where(Notification.notification_id == notification_id)).scalar_one_or_none()
    if notification is None:
        return None
    deliveries = db.execute(select(NotificationDelivery).where(NotificationDelivery.notification_id == notification_id)).scalars().all()
    result_deliveries = []
    for item in deliveries:
        device = db.execute(select(Device).where(Device.device_id == item.device_id)).scalar_one_or_none()
        result_deliveries.append(
            {
                "device_id": item.device_id,
                "device_name": device.device_name if device else "",
                "received": item.received,
                "displayed": item.displayed,
                "spoken": item.spoken,
                "failed": item.failed,
                "error_message": item.error_message,
            }
        )
    return {
        "notification_id": notification.notification_id,
        "sender_user_id": notification.sender_user_id,
        "title": notification.title,
        "content": notification.content,
        "created_at": notification.created_at.isoformat(),
        "deliveries": result_deliveries,
    }
