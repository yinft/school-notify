import asyncio
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from starlette.websockets import WebSocketDisconnect

from app.api.deps import auth as auth_deps
from app.api.routes import auth as auth_route
from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.models import AuthSession, User
from app.services.auth_sessions import create_auth_session, get_or_create_user_by_openid
from app.services import store as store_module
from app.services.device_connections import device_connections
from app.services.store import store
from app.services.wechat_auth import build_device_token, build_session_token

store_module.redis_service._client = None


client = TestClient(app)


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def auth_headers(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {build_session_token(user_id)}"}


def active_auth_headers(user_id: str) -> dict[str, str]:
    token = build_session_token(user_id)
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid=user_id)
        create_auth_session(session, user=user, session_token=token)
        session.commit()
    return {"Authorization": f"Bearer {token}"}


def device_auth_headers(device_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {build_device_token(device_id)}"}


def setup_function() -> None:
    Base.metadata.create_all(bind=engine)
    store.reset()
    with SessionLocal() as session:
        session.execute(delete(AuthSession))
        session.execute(delete(User))
        session.commit()


def test_auth_login_returns_wechat_openid_session(monkeypatch) -> None:
    monkeypatch.setattr(
        auth_route,
        "exchange_code_for_session",
        lambda code: {
            "openid": "wx-openid-001",
            "session_key": "session-key-001",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={"code": "wx-code-001"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "wx-openid-001",
        "session_token": build_session_token("wx-openid-001"),
        "auth_provider": "wechat",
    }


def test_auth_login_returns_bad_gateway_when_openid_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        auth_route,
        "exchange_code_for_session",
        lambda code: {"errcode": 40029, "errmsg": "invalid code"},
    )

    response = client.post(
        "/api/auth/login",
        json={"code": "bad-code"},
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "wechat login failed"}


def test_auth_whoami_rejects_signed_but_unknown_session() -> None:
    response = client.get("/api/auth/current_user", headers=auth_headers("wx-openid-001"))

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid session token"}


def test_auth_whoami_returns_current_user_from_active_session(monkeypatch) -> None:
    monkeypatch.setattr(
        auth_route,
        "exchange_code_for_session",
        lambda code: {
            "openid": "wx-openid-001",
            "session_key": "session-key-001",
        },
    )
    login_response = client.post("/api/auth/login", json={"code": "wx-code-001"})

    response = client.get(
        "/api/auth/current_user",
        headers={"Authorization": f"Bearer {login_response.json()['session_token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "wx-openid-001",
        "session_token": build_session_token("wx-openid-001"),
        "auth_provider": "wechat",
    }


def test_auth_logout_revokes_current_session(monkeypatch) -> None:
    monkeypatch.setattr(
        auth_route,
        "exchange_code_for_session",
        lambda code: {
            "openid": "wx-openid-001",
            "session_key": "session-key-001",
        },
    )
    login_response = client.post("/api/auth/login", json={"code": "wx-code-001"})
    token = login_response.json()["session_token"]

    logout_response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    whoami_response = client.get("/api/auth/current_user", headers={"Authorization": f"Bearer {token}"})

    assert logout_response.status_code == 204
    assert whoami_response.status_code == 401
    assert whoami_response.json() == {"detail": "invalid session token"}


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
    assert register_payload["location_label"] == ""
    assert register_payload["client_version"] == "0.1.0"
    assert register_payload["status"] == "online"
    assert parse_timestamp(register_payload["last_seen_at"])

    list_response = client.get("/api/devices")

    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert len(list_payload["items"]) == 1
    assert list_payload["items"][0]["device_id"] == "device-001"
    assert list_payload["items"][0]["location_label"] == ""
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

    heartbeat_response = client.post("/api/devices/device-001/heartbeat", headers=device_auth_headers("device-001"))

    assert heartbeat_response.status_code == 200
    heartbeat_payload = heartbeat_response.json()
    assert heartbeat_payload["device_id"] == "device-001"
    assert heartbeat_payload["status"] == "online"
    assert parse_timestamp(heartbeat_payload["last_seen_at"]) >= registered_at


def test_device_heartbeat_returns_not_found_for_unknown_device() -> None:
    response = client.post("/api/devices/missing-device/heartbeat", headers=device_auth_headers("missing-device"))

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
        headers=device_auth_headers("device-001"),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["device_id"] == "device-001"
    assert payload["expires_in_seconds"] == 30
    assert len(payload["code"]) == 6
    assert payload["code"].isdigit()


def test_binding_code_rotates_immediately_for_same_device() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )

    first = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
        headers=device_auth_headers("device-001"),
    )
    second = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
        headers=device_auth_headers("device-001"),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["code"] != first.json()["code"]


def test_previous_binding_code_becomes_invalid_after_rotation() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )

    first = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
        headers=device_auth_headers("device-001"),
    )
    second = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
        headers=device_auth_headers("device-001"),
    )

    response = client.get(
        f"/api/bindings/code/{first.json()['code']}/device",
        headers=active_auth_headers("user-001"),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["code"] != second.json()["code"]
    assert response.status_code == 404
    assert response.json() == {"detail": "binding code not found"}


def test_binding_code_returns_not_found_for_unknown_device() -> None:
    response = client.post(
        "/api/bindings/code",
        json={"device_id": "missing-device"},
        headers=device_auth_headers("missing-device"),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}


def test_device_heartbeat_requires_matching_device_token() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )

    missing = client.post("/api/devices/device-001/heartbeat")
    mismatched = client.post("/api/devices/device-001/heartbeat", headers=device_auth_headers("device-002"))

    assert missing.status_code == 401
    assert mismatched.status_code == 403


def test_binding_code_requires_matching_device_token() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )

    missing = client.post("/api/bindings/code", json={"device_id": "device-001"})
    mismatched = client.post(
        "/api/bindings/code",
        json={"device_id": "device-001"},
        headers=device_auth_headers("device-002"),
    )

    assert missing.status_code == 401
    assert mismatched.status_code == 403


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
        headers=device_auth_headers("device-001"),
    )

    bind_response = client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
    )

    assert bind_response.status_code == 201
    assert bind_response.json() == {
        "user_id": "user-001",
        "device_id": "device-001",
    }

    devices_response = client.get(
        "/api/users/user-001/devices",
        headers=active_auth_headers("user-001"),
    )

    assert devices_response.status_code == 200
    payload = devices_response.json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["device_id"] == "device-001"


def test_user_can_update_bound_device_name_and_location() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "editable-device-001",
            "device_name": "DESKTOP-ABC123",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "editable-device-001"},
        headers=device_auth_headers("editable-device-001"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "editable-user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("editable-user-001"),
    )

    response = client.patch(
        "/api/users/editable-user-001/devices/editable-device-001",
        json={"device_name": "三年级一班通知屏", "location_label": "三年级一班教室"},
        headers=active_auth_headers("editable-user-001"),
    )
    devices_response = client.get(
        "/api/users/editable-user-001/devices",
        headers=active_auth_headers("editable-user-001"),
    )

    assert response.status_code == 200
    assert response.json()["device_name"] == "三年级一班通知屏"
    assert response.json()["location_label"] == "三年级一班教室"
    assert devices_response.json()["items"][0]["device_name"] == "三年级一班通知屏"
    assert devices_response.json()["items"][0]["location_label"] == "三年级一班教室"


def test_user_device_update_forbids_cross_user_access() -> None:
    response = client.patch(
        "/api/users/user-001/devices/device-001",
        json={"device_name": "新名称"},
        headers=active_auth_headers("another-user"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "forbidden"}


def test_binding_code_preview_returns_registered_device_info() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "preview-device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "preview-device-001"},
        headers=device_auth_headers("preview-device-001"),
    )

    response = client.get(
        f"/api/bindings/code/{bind_code_response.json()['code']}/device",
        headers=active_auth_headers("preview-user-001"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "device_id": "preview-device-001",
        "device_name": "值班室电脑",
        "location_label": "",
        "client_version": "0.1.0",
        "status": "online",
        "last_seen_at": response.json()["last_seen_at"],
        "device_token": "",
    }


def test_binding_can_update_device_name_and_location() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "metadata-device-001",
            "device_name": "DESKTOP-ABC123",
            "client_version": "0.1.0",
        },
    )
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "metadata-device-001"},
        headers=device_auth_headers("metadata-device-001"),
    )

    bind_response = client.post(
        "/api/bindings",
        json={
            "user_id": "metadata-user-001",
            "code": bind_code_response.json()["code"],
            "device_name": "三年级一班通知屏",
            "location_label": "三年级一班教室",
        },
        headers=active_auth_headers("metadata-user-001"),
    )
    devices_response = client.get(
        "/api/users/metadata-user-001/devices",
        headers=active_auth_headers("metadata-user-001"),
    )

    assert bind_response.status_code == 201
    assert devices_response.status_code == 200
    assert devices_response.json()["items"][0]["device_name"] == "三年级一班通知屏"
    assert devices_response.json()["items"][0]["location_label"] == "三年级一班教室"


def test_user_can_unbind_device() -> None:
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
        headers=device_auth_headers("device-001"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
    )

    response = client.delete(
        "/api/bindings/device-001",
        params={"user_id": "user-001"},
        headers=active_auth_headers("user-001"),
    )

    devices_response = client.get(
        "/api/users/user-001/devices",
        headers=active_auth_headers("user-001"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "user-001",
        "device_id": "device-001",
    }
    assert devices_response.status_code == 200
    assert devices_response.json() == {"items": []}


def test_binding_returns_not_found_for_unknown_code() -> None:
    response = client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": "999999",
        },
        headers=active_auth_headers("user-001"),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "binding code not found"}


def test_binding_prefers_redis_code_cache(monkeypatch) -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "client_version": "0.1.0",
        },
    )

    monkeypatch.setattr(store_module.redis_service, "get_bind_device_id", lambda code: "device-001")
    monkeypatch.setattr(store_module.redis_service, "consume_bind_code", lambda code: None)

    response = client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": "REDIS-CODE",
        },
        headers=active_auth_headers("user-001"),
    )

    assert response.status_code == 201
    assert response.json() == {
        "user_id": "user-001",
        "device_id": "device-001",
    }


def test_binding_code_can_only_be_used_once() -> None:
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
        headers=device_auth_headers("device-001"),
    )
    code = bind_code_response.json()["code"]

    first = client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": code,
        },
        headers=active_auth_headers("user-001"),
    )
    second = client.post(
        "/api/bindings",
        json={
            "user_id": "user-002",
            "code": code,
        },
        headers=active_auth_headers("user-002"),
    )

    assert first.status_code == 201
    assert second.status_code == 404
    assert second.json() == {"detail": "binding code not found"}


def test_user_devices_require_valid_session_token() -> None:
    response = client.get("/api/users/user-001/devices")

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid session token"}


def test_user_devices_forbid_cross_user_access() -> None:
    response = client.get(
        "/api/users/user-001/devices",
        headers=active_auth_headers("another-user"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "forbidden"}


def test_binding_forbids_mismatched_user_and_token() -> None:
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
        headers=device_auth_headers("device-001"),
    )

    response = client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("another-user"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "forbidden"}


def test_notifications_forbid_mismatched_user_and_token() -> None:
    response = client.post(
        "/api/notifications",
        json={
            "sender_user_id": "user-001",
            "title": "Test",
            "content": "Hello world",
            "level": "normal",
            "device_ids": ["device-001"],
        },
        headers=active_auth_headers("another-user"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "forbidden"}


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
        headers=device_auth_headers("device-001"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
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
        headers=active_auth_headers("user-001"),
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
        headers=active_auth_headers("user-001"),
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
        headers=active_auth_headers("user-001"),
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
        headers=device_auth_headers("device-001"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
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
        headers=active_auth_headers("user-001"),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "device offline"}


def test_ws_placeholder_sends_connected_event(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "set_device_online", lambda device_id, ttl=90: None)
    monkeypatch.setattr(store_module.redis_service, "set_device_offline", lambda device_id: None)

    client.post(
        "/api/devices/register",
        json={
            "device_id": "demo-device-1",
            "device_name": "Demo设备",
            "client_version": "0.1.0",
        },
    )
    token = build_device_token("demo-device-1")
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid="demo-user")
        create_auth_session(session, user=user, session_token=token)
        session.commit()

    with client.websocket_connect(f"/ws/devices/demo-device-1?token={token}") as websocket:
        payload = websocket.receive_json()

    assert payload == {
        "event": "connected",
        "device_id": "demo-device-1",
        "status": "online",
    }


def test_binding_code_requires_registered_device() -> None:
    response = client.post(
        "/api/bindings/code",
        json={"device_id": "unknown-device"},
        headers=device_auth_headers("unknown-device"),
    )
    assert response.status_code == 404


def test_notification_offline_device_returns_409_when_redis_and_db_offline(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "is_device_online", lambda device_id: False)

    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-offline",
            "device_name": "离线设备",
            "client_version": "0.1.0",
        },
    )
    store.set_device_status(device_id="device-offline", status="offline")
    bind_code_response = client.post(
        "/api/bindings/code",
        json={"device_id": "device-offline"},
        headers=device_auth_headers("device-offline"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
    )

    response = client.post(
        "/api/notifications",
        json={
            "sender_user_id": "user-001",
            "title": "Test",
            "content": "Hello",
            "level": "normal",
            "device_ids": ["device-offline"],
        },
        headers=active_auth_headers("user-001"),
    )
    assert response.status_code == 409


def test_websocket_receives_notification_created_event(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "set_device_online", lambda device_id, ttl=90: None)
    monkeypatch.setattr(store_module.redis_service, "set_device_offline", lambda device_id: None)

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
        headers=device_auth_headers("device-001"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
    )

    ws_token = build_device_token("device-001")
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid="user-001")
        create_auth_session(session, user=user, session_token=ws_token)
        session.commit()

    with client.websocket_connect(f"/ws/devices/device-001?token={ws_token}") as websocket:
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
            headers=active_auth_headers("user-001"),
        )
        pushed = websocket.receive_json()

    assert connected == {
        "event": "connected",
        "device_id": "device-001",
        "status": "online",
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


def test_websocket_receipt_updates_notification_delivery_state(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "set_device_online", lambda device_id, ttl=90: None)
    monkeypatch.setattr(store_module.redis_service, "set_device_offline", lambda device_id: None)

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
        headers=device_auth_headers("device-001"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
    )

    ws_token = build_device_token("device-001")
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid="user-001")
        create_auth_session(session, user=user, session_token=ws_token)
        session.commit()

    with client.websocket_connect(f"/ws/devices/device-001?token={ws_token}") as websocket:
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
            headers=active_auth_headers("user-001"),
        )
        pushed = websocket.receive_json()
        websocket.send_json(
            {
                "event": "receipt_displayed",
                "notification_id": pushed["payload"]["notification_id"],
            }
        )

    response = client.get(
        "/api/notifications",
        params={"sender_user_id": "user-001"},
        headers=active_auth_headers("user-001"),
    )
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["deliveries"][0]["displayed"] is True


def test_notification_list_supports_pagination() -> None:
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
        headers=device_auth_headers("device-001"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
    )

    for i in range(5):
        client.post(
            "/api/notifications",
            json={
                "sender_user_id": "user-001",
                "title": f"通知{i}",
                "content": "内容",
                "level": "normal",
                "device_ids": ["device-001"],
            },
            headers=active_auth_headers("user-001"),
        )

    page1 = client.get(
        "/api/notifications",
        params={"sender_user_id": "user-001", "limit": 2, "offset": 0},
        headers=active_auth_headers("user-001"),
    )
    assert page1.status_code == 200
    assert len(page1.json()["items"]) == 2
    assert page1.json()["total"] == 5

    page2 = client.get(
        "/api/notifications",
        params={"sender_user_id": "user-001", "limit": 2, "offset": 2},
        headers=active_auth_headers("user-001"),
    )
    assert page2.status_code == 200
    assert len(page2.json()["items"]) == 2

    page3 = client.get(
        "/api/notifications",
        params={"sender_user_id": "user-001", "limit": 2, "offset": 4},
        headers=active_auth_headers("user-001"),
    )
    assert page3.status_code == 200
    assert len(page3.json()["items"]) == 1


def test_user_can_update_profile() -> None:
    token = build_session_token("profile-user")
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid="profile-user")
        create_auth_session(session, user=user, session_token=token)
        session.commit()

    response = client.patch(
        "/api/users/me",
        json={"nickname": "张老师", "avatar_url": "https://example.com/avatar.jpg"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "张老师"
    assert response.json()["avatar_url"] == "https://example.com/avatar.jpg"


def test_user_profile_requires_auth() -> None:
    response = client.patch(
        "/api/users/me",
        json={"nickname": "测试"},
    )
    assert response.status_code == 401


def test_notifications_query_returns_records_and_receipts(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "set_device_online", lambda device_id, ttl=90: None)
    monkeypatch.setattr(store_module.redis_service, "set_device_offline", lambda device_id: None)

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
        headers=device_auth_headers("device-001"),
    )
    client.post(
        "/api/bindings",
        json={
            "user_id": "user-001",
            "code": bind_code_response.json()["code"],
        },
        headers=active_auth_headers("user-001"),
    )

    ws_token = build_device_token("device-001")
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid="user-001")
        create_auth_session(session, user=user, session_token=ws_token)
        session.commit()

    with client.websocket_connect(f"/ws/devices/device-001?token={ws_token}") as websocket:
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
            headers=active_auth_headers("user-001"),
        )
        pushed = websocket.receive_json()
        websocket.send_json(
            {
                "event": "receipt_displayed",
                "notification_id": pushed["payload"]["notification_id"],
            }
        )

    response = client.get(
        "/api/notifications",
        params={"sender_user_id": "user-001"},
        headers=active_auth_headers("user-001"),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["notification_id"] == "notification-1"
    assert payload["items"][0]["sender_user_id"] == "user-001"
    assert payload["items"][0]["title"] == "紧急通知"
    assert payload["items"][0]["content"] == "请立即集合"
    assert payload["items"][0]["level"] == "urgent"
    assert payload["items"][0]["target_count"] == 1
    assert payload["items"][0]["created_at"]
    assert payload["items"][0]["deliveries"] == [
        {
            "device_id": "device-001",
            "device_name": "值班室电脑",
            "location_label": "",
            "received": False,
            "displayed": True,
            "spoken": False,
            "failed": False,
            "error_message": None,
        }
    ]


def test_auth_session_cached_in_redis(monkeypatch) -> None:
    local_cache: dict[str, str] = {}

    def fake_cache(*, session_token, user_id, ttl_seconds):
        local_cache[session_token] = user_id

    def fake_get(session_token):
        return local_cache.get(session_token)

    monkeypatch.setattr(store_module.redis_service, "cache_auth_session", fake_cache)
    monkeypatch.setattr(store_module.redis_service, "get_cached_auth_user", fake_get)

    token = build_session_token("cache-user")
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid="cache-user")
        create_auth_session(session, user=user, session_token=token)
        session.commit()

    response = client.get(
        "/api/auth/current_user",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "cache-user" in local_cache.values()


def test_device_heartbeat_sets_redis_online(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "set_device_online", lambda device_id, ttl=90: None)

    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-hb",
            "device_name": "心跳测试设备",
            "client_version": "0.1.0",
        },
    )

    cached = {}

    def fake_set_online(device_id, ttl=90):
        cached["device_id"] = device_id
        cached["ttl"] = ttl

    monkeypatch.setattr(store_module.redis_service, "set_device_online", fake_set_online)

    response = client.post("/api/devices/device-hb/heartbeat", headers=device_auth_headers("device-hb"))
    assert response.status_code == 200
    assert cached["device_id"] == "device-hb"
    assert cached["ttl"] > 0


def test_device_online_status_reads_redis(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "is_device_online", lambda device_id: True)
    monkeypatch.setattr(store_module.redis_service, "get_device_last_seen", lambda device_id: "2026-04-22T12:00:00Z")

    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-ol",
            "device_name": "在线状态设备",
            "client_version": "0.1.0",
        },
    )

    response = client.get("/api/devices")
    assert response.status_code == 200
    items = response.json()["items"]
    target = next(d for d in items if d["device_id"] == "device-ol")
    assert target["status"] == "online"


def test_auth_whoami_refreshes_cached_session_ttl(monkeypatch) -> None:
    token = build_session_token("cache-hit-user")
    captured: dict[str, object] = {}

    monkeypatch.setattr(store_module.redis_service, "get_cached_auth_user", lambda session_token: "cache-hit-user")

    def fake_cache_auth_session(*, session_token: str, user_id: str, ttl_seconds: int) -> None:
        captured["session_token"] = session_token
        captured["user_id"] = user_id
        captured["ttl_seconds"] = ttl_seconds

    monkeypatch.setattr(store_module.redis_service, "cache_auth_session", fake_cache_auth_session)

    def fail_db_lookup(*args, **kwargs):
        raise AssertionError("should not hit DB when auth session cache is valid")

    monkeypatch.setattr(auth_deps, "get_active_session_by_token", fail_db_lookup)

    response = client.get(
        "/api/auth/current_user",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert captured["session_token"] == token
    assert captured["user_id"] == "cache-hit-user"
    assert int(captured["ttl_seconds"]) > 0


def test_websocket_requires_valid_token() -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/devices/device-001?token=invalid-token"):
            pass


def test_websocket_accepts_valid_token() -> None:
    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-ws",
            "device_name": "WS鉴权设备",
            "client_version": "0.1.0",
        },
    )
    token = build_device_token("device-ws")
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid="ws-user")
        create_auth_session(session, user=user, session_token=token)
        session.commit()

    with client.websocket_connect(f"/ws/devices/device-ws?token={token}") as websocket:
        msg = websocket.receive_json()
        assert msg["event"] == "connected"


def test_websocket_disconnect_sets_device_offline(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "set_device_online", lambda device_id, ttl=90: None)

    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-dc",
            "device_name": "断连测试设备",
            "client_version": "0.1.0",
        },
    )
    token = build_device_token("device-dc")
    with SessionLocal() as session:
        user = get_or_create_user_by_openid(session, openid="dc-user")
        create_auth_session(session, user=user, session_token=token)
        session.commit()

    offline_called = {"flag": False}

    def fake_set_offline(device_id):
        if device_id == "device-dc":
            offline_called["flag"] = True

    monkeypatch.setattr(store_module.redis_service, "set_device_offline", fake_set_offline)

    with client.websocket_connect(f"/ws/devices/device-dc?token={token}"):
        pass

    assert offline_called["flag"]
    assert store.list_devices()[0].status == "offline"


def test_stale_websocket_send_marks_device_offline_and_failed(monkeypatch) -> None:
    monkeypatch.setattr(store_module.redis_service, "set_device_online", lambda device_id, ttl=90: None)
    monkeypatch.setattr(store_module.redis_service, "set_device_offline", lambda device_id: None)

    client.post(
        "/api/devices/register",
        json={
            "device_id": "device-stale",
            "device_name": "失效连接设备",
            "client_version": "0.1.0",
        },
    )

    class FailingWebSocket:
        async def accept(self):
            return None

        async def send_json(self, payload):
            raise RuntimeError("socket disconnected")

    asyncio.run(device_connections.connect(device_id="device-stale", websocket=FailingWebSocket()))

    failed_device_ids = asyncio.run(
        device_connections.send_notifications(
            deliveries=[
                {
                    "device_id": "device-stale",
                    "payload": {
                        "notification_id": "notification-stale",
                        "title": "Test",
                        "content": "Hello",
                        "level": "normal",
                    },
                }
            ]
        )
    )

    assert failed_device_ids == ["device-stale"]
    assert store.list_devices()[0].status == "offline"
