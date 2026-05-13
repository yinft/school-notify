from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Device, Notification, User


def get_dashboard_summary(db: Session) -> dict[str, int]:
    device_count = db.execute(select(func.count()).select_from(Device)).scalar_one()
    online_device_count = db.execute(select(func.count()).select_from(Device).where(Device.status == "online")).scalar_one()
    user_count = db.execute(select(func.count()).select_from(User)).scalar_one()
    notification_count = db.execute(select(func.count()).select_from(Notification)).scalar_one()
    today = datetime.now().date()
    notifications = db.execute(select(Notification)).scalars().all()
    notification_trend = []
    for days_ago in range(6, -1, -1):
        target_day = today - timedelta(days=days_ago)
        notification_trend.append(
            {
                "date": target_day.isoformat(),
                "count": sum(1 for item in notifications if item.created_at.date() == target_day),
            }
        )

    device_status_ratio = {
        "online": online_device_count,
        "offline": max(device_count - online_device_count, 0),
    }

    devices = db.execute(select(Device)).scalars().all()
    version_counts: dict[str, int] = {}
    for device in devices:
        version_counts[device.client_version] = version_counts.get(device.client_version, 0) + 1

    version_distribution = [
        {"client_version": version, "device_count": count}
        for version, count in sorted(version_counts.items())
    ]

    return {
        "device_count": device_count,
        "online_device_count": online_device_count,
        "user_count": user_count,
        "notification_count": notification_count,
        "notification_trend": notification_trend,
        "device_status_ratio": device_status_ratio,
        "version_distribution": version_distribution,
    }
