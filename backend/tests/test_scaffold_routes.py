from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.services.store import store


client = TestClient(app)


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def setup_function() -> None:
    store.reset()


def test_auth_whoami_returns_placeholder_user() -> None:
    response = client.get("/api/auth/whoami")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "demo-user",
        "status": "placeholder",
    }


def test_devices_returns_empty_list() -> None:
    response = client.get("/api/devices")

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_device_registration_is_reflected_in_device_list() -> None:
    register_response = client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )

    assert register_response.status_code == 201
    register_payload = register_response.json()
    assert register_payload["device_id"] == "device-001"
    assert register_payload["device_name"] == "值班室电脑"
    assert register_payload["client_version"] == "0.1.0"
    assert register_payload["status"] == "online"
    assert parse_timestamp(register_payload["last_seen_at"])

    list_response = client.get("/api/devices")

    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert len(list_payload["items"]) == 1
    assert list_payload["items"][0]["device_id"] == "device-001"
    assert list_payload["items"][0]["status"] == "online"
    assert parse_timestamp(list_payload["items"][0]["last_seen_at"])


def test_device_heartbeat_refreshes_last_seen() -> None:
    register_response = client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )
    registered_at = parse_timestamp(register_response.json()["last_seen_at"])

    heartbeat_response = client.post("/api/devices/device-001/heartbeat")

    assert heartbeat_response.status_code == 200
    heartbeat_payload = heartbeat_response.json()
    assert heartbeat_payload["device_id"] == "device-001"
    assert heartbeat_payload["status"] == "online"
    assert parse_timestamp(heartbeat_payload["last_seen_at"]) >= registered_at


def test_device_heartbeat_returns_not_found_for_unknown_device() -> None:
    response = client.post("/api/devices/missing-device/heartbeat")

    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}


def test_binding_code_returns_generated_code() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )

    response = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["device_id"] == "device-001"
    assert payload["expires_in_seconds"] == 300
    assert len(payload["code"]) == 6
    assert payload["code"].isdigit()


def test_binding_code_returns_not_found_for_unknown_device() -> None:
    response = client.post(
        "/api/bindings/code",
        json={"device_id": "missing-device"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}


def test_user_can_bind_device_by_code_and_query_bound_devices() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
    )

    bind_response = client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
    )

    assert bind_response.status_code == 201
    assert bind_response.json() == {
        "user_id": "user-001",
        "device_id": "device-001",
    }

    devices_response = client.get("/api/users/user-001/devices")

    assert devices_response.status_code == 200
    payload = devices_response.json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["device_id"] == "device-001"


def test_binding_returns_not_found_for_unknown_code() -> None:
    response = client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": "999999",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "binding code not found"}


def test_notifications_returns_placeholder_payload() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
    )

    response = client.post(
        "/api/notifications",
        json={
            "sender_user_id": "user-001",
            "title": "Test",
            "content": "Hello world",
            "level": "normal",
            "device_ids": ["device-001"],
        },
    )

    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted",
        "target_count": 1,
    }


def test_notifications_return_not_found_for_unknown_device() -> None:
    response = client.post(
        "/api/notifications",
        json={
            "sender_user_id": "user-001",
            "title": "Test",
            "content": "Hello world",
            "level": "normal",
            "device_ids": ["missing-device"],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}


def test_notifications_return_forbidden_for_unbound_device() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )

    response = client.post(
        "/api/notifications",
        json={
            "sender_user_id": "user-001",
            "title": "Test",
            "content": "Hello world",
            "level": "normal",
            "device_ids": ["device-001"],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "device not bound to user"}


def test_notifications_return_conflict_for_offline_device() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
    )
    store.set_device_status(device_id="device-001", status="offline")

    response = client.post(
        "/api/notifications",
        json={
            "sender_user_id": "user-001",
            "title": "Test",
            "content": "Hello world",
            "level": "normal",
            "device_ids": ["device-001"],
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "device offline"}


def test_ws_placeholder_sends_connected_event() -> None:
    with client.websocket_connect("/ws/devices/demo-device-1") as websocket:
        payload = websocket.receive_json()

    assert payload == {
        "event": "connected",
        "device_id": "demo-device-1",
        "status": "placeholder",
    }


def test_websocket_receives_notification_created_event() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
    )

    with client.websocket_connect("/ws/devices/device-001") as websocket:
        connected = websocket.receive_json()

        response = client.post(
            "/api/notifications",
            json={
                "sender_user_id": "user-001",
                "title": "紧急通知",
                "content": "请立即集合",
                "level": "urgent",
                "device_ids": ["device-001"],
            },
        )
        pushed = websocket.receive_json()

    assert connected == {
        "event": "connected",
        "device_id": "device-001",
        "status": "placeholder",
    }
    assert response.status_code == 202
    assert pushed == {
        "event": "notification_created",
        "device_id": "device-001",
        "payload": {
            "notification_id": "notification-1",
            "title": "紧急通知",
            "content": "请立即集合",
            "level": "urgent",
        },
    }


def test_websocket_receipt_updates_notification_delivery_state() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
    )

    with client.websocket_connect("/ws/devices/device-001") as websocket:
        websocket.receive_json()
        client.post(
            "/api/notifications",
            json={
                "sender_user_id": "user-001",
                "title": "紧急通知",
                "content": "请立即集合",
                "level": "urgent",
                "device_ids": ["device-001"],
            },
        )
        pushed = websocket.receive_json()
        websocket.send_json(
            {
                "event": "receipt_displayed",
                "notification_id": pushed["payload"]["notification_id"],
            }
        )

    assert store.delivery_receipts["device-001"]["notification-1"]["displayed"] is True


def test_notifications_query_returns_records_and_receipts() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
    )

    with client.websocket_connect("/ws/devices/device-001") as websocket:
        websocket.receive_json()
        client.post(
            "/api/notifications",
            json={
                "sender_user_id": "user-001",
                "title": "紧急通知",
                "content": "请立即集合",
                "level": "urgent",
                "device_ids": ["device-001"],
            },
        )
        pushed = websocket.receive_json()
        websocket.send_json(
            {
                "event": "receipt_displayed",
                "notification_id": pushed["payload"]["notification_id"],
            }
        )

    response = client.get("/api/notifications", params={"sender_user_id": "user-001"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "notification_id": "notification-1",
                "sender_user_id": "user-001",
                "title": "紧急通知",
                "content": "请立即集合",
                "level": "urgent",
                "target_count": 1,
                "deliveries": [
                    {
                        "device_id": "device-001",
                        "received": False,
                        "displayed": True,
                        "spoken": False,
                    }
                ],
            }
        ]
    }
