from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.models import AdminSession, AdminUser, Device, Notification, NotificationDelivery, User, UserDevice


client = TestClient(app)


def setup_function() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.execute(delete(NotificationDelivery))
        session.execute(delete(Notification))
        session.execute(delete(UserDevice))
        session.execute(delete(Device))
        session.execute(delete(User))
        session.execute(delete(AdminSession))
        session.execute(delete(AdminUser))
        session.commit()


def admin_headers() -> dict[str, str]:
    with SessionLocal() as session:
        existing = session.query(AdminUser).filter(AdminUser.username == "admin").one_or_none()
        if existing is None:
            session.add(
                AdminUser(
                    username="admin",
                    password_hash="plain$pass123456",
                    display_name="系统管理员",
                )
            )
        session.commit()

    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "pass123456"},
    )
    return {"Authorization": f"Bearer {response.json()['session_token']}"}


def seed_admin_query_data() -> None:
    with SessionLocal() as session:
        session.add_all([
            User(user_id="user-001", openid="user-001", nickname="张三", avatar_url="https://example.com/a.png"),
            User(user_id="user-002", openid="user-002", nickname="李四", avatar_url="https://example.com/b.png"),
            User(user_id="user-003", openid="user-003", nickname="王五", avatar_url="https://example.com/c.png"),
            Device(device_id="device-001", device_name="值班室电脑", location_label="值班室", client_version="1.0.0", status="online"),
            Device(device_id="device-002", device_name="办公室电脑", location_label="办公室", client_version="1.1.0", status="offline"),
            Device(device_id="device-003", device_name="会议室电脑", location_label="会议室", client_version="1.1.0", status="online"),
            UserDevice(user_id="user-001", device_id="device-001"),
            UserDevice(user_id="user-001", device_id="device-002"),
            UserDevice(user_id="user-002", device_id="device-003"),
        ])
        session.add_all([
            Notification(
                notification_id="notification-001",
                sender_user_id="user-001",
                title="值班提醒",
                content="请查看今日值班安排",
                level="info",
                duration_seconds=30,
                tts_enabled=True,
                tts_repeat_count=1,
                target_count=2,
            ),
            Notification(
                notification_id="notification-002",
                sender_user_id="user-002",
                title="会议提醒",
                content="请准时参加会议",
                level="info",
                duration_seconds=30,
                tts_enabled=True,
                tts_repeat_count=1,
                target_count=1,
            ),
        ])
        session.add_all([
            NotificationDelivery(notification_id="notification-001", device_id="device-001", received=True, displayed=True, spoken=True),
            NotificationDelivery(notification_id="notification-001", device_id="device-002", received=False, displayed=False, spoken=False, failed=True, error_message="device offline"),
            NotificationDelivery(notification_id="notification-002", device_id="device-003", received=True, displayed=True, spoken=False, failed=False, error_message=None),
        ])
        session.commit()


def test_admin_dashboard_summary_returns_counts() -> None:
    seed_admin_query_data()

    response = client.get("/api/admin/dashboard/summary", headers=admin_headers())

    assert response.status_code == 200
    payload = response.json()
    assert payload["device_count"] == 3
    assert payload["online_device_count"] == 2
    assert payload["user_count"] == 3
    assert payload["notification_count"] == 2
    assert len(payload["notification_trend"]) == 7
    assert payload["device_status_ratio"] == {"online": 2, "offline": 1}
    assert payload["version_distribution"] == [
        {"client_version": "1.0.0", "device_count": 1},
        {"client_version": "1.1.0", "device_count": 2},
    ]


def test_admin_dashboard_summary_supports_30_day_trend() -> None:
    seed_admin_query_data()

    response = client.get("/api/admin/dashboard/summary?trend_days=30", headers=admin_headers())

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["notification_trend"]) == 30


def test_admin_dashboard_notification_trend_endpoint_returns_selected_range() -> None:
    seed_admin_query_data()

    response = client.get("/api/admin/dashboard/notification-trend?days=30", headers=admin_headers())

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 30
    assert set(payload["items"][0].keys()) == {"date", "count"}


def test_admin_device_list_and_detail() -> None:
    seed_admin_query_data()

    list_response = client.get("/api/admin/devices", headers=admin_headers())
    detail_response = client.get("/api/admin/devices/device-001", headers=admin_headers())

    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 3
    assert detail_response.status_code == 200
    assert detail_response.json()["device_id"] == "device-001"
    assert len(detail_response.json()["bound_users"]) == 1
    assert len(detail_response.json()["recent_notifications"]) == 1

    filtered_response = client.get("/api/admin/devices?status=online&keyword=值班", headers=admin_headers())
    assert filtered_response.status_code == 200
    assert [item["device_id"] for item in filtered_response.json()["items"]] == ["device-001"]

    paged_response = client.get("/api/admin/devices?page=2&page_size=1", headers=admin_headers())
    assert paged_response.status_code == 200
    assert paged_response.json()["total"] == 3
    assert paged_response.json()["page"] == 2
    assert paged_response.json()["page_size"] == 1
    assert [item["device_id"] for item in paged_response.json()["items"]] == ["device-002"]


def test_admin_can_update_device_and_unbind_user() -> None:
    seed_admin_query_data()

    update_response = client.patch(
        "/api/admin/devices/device-001",
        headers=admin_headers(),
        json={"device_name": "值班室主机", "location_label": "一楼值班室"},
    )
    unbind_response = client.delete(
        "/api/admin/devices/device-001/bindings/user-001",
        headers=admin_headers(),
    )

    assert update_response.status_code == 200
    assert update_response.json()["device_name"] == "值班室主机"
    assert update_response.json()["location_label"] == "一楼值班室"
    assert unbind_response.status_code == 204


def test_admin_user_list_and_detail() -> None:
    seed_admin_query_data()

    list_response = client.get("/api/admin/users", headers=admin_headers())
    detail_response = client.get("/api/admin/users/user-001", headers=admin_headers())

    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 3
    assert detail_response.status_code == 200
    assert detail_response.json()["user_id"] == "user-001"
    assert len(detail_response.json()["devices"]) == 2
    assert len(detail_response.json()["recent_notifications"]) == 1

    filtered_response = client.get("/api/admin/users?keyword=张三", headers=admin_headers())
    assert filtered_response.status_code == 200
    assert [item["user_id"] for item in filtered_response.json()["items"]] == ["user-001"]

    paged_response = client.get("/api/admin/users?page=2&page_size=1", headers=admin_headers())
    assert paged_response.status_code == 200
    assert paged_response.json()["total"] == 3
    assert [item["user_id"] for item in paged_response.json()["items"]] == ["user-002"]


def test_admin_notification_list_and_detail() -> None:
    seed_admin_query_data()

    list_response = client.get("/api/admin/notifications", headers=admin_headers())
    detail_response = client.get("/api/admin/notifications/notification-001", headers=admin_headers())

    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 2
    assert list_response.json()["items"][1]["success_count"] == 1
    assert list_response.json()["items"][1]["failed_count"] == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["notification_id"] == "notification-001"
    assert len(detail_response.json()["deliveries"]) == 2

    filtered_response = client.get("/api/admin/notifications?keyword=值班&sender_user_id=user-001", headers=admin_headers())
    assert filtered_response.status_code == 200
    assert [item["notification_id"] for item in filtered_response.json()["items"]] == ["notification-001"]

    paged_response = client.get("/api/admin/notifications?page=2&page_size=1", headers=admin_headers())
    assert paged_response.status_code == 200
    assert paged_response.json()["total"] == 2
    assert [item["notification_id"] for item in paged_response.json()["items"]] == ["notification-001"]
