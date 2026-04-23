from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.db import SessionLocal
from app.services.auth_sessions import get_cached_auth_user_id
from app.services.device_connections import device_connections
from app.services.redis_service import redis_service
from app.services.store import store
from app.services.wechat_auth import WeChatLoginError, parse_session_token


router = APIRouter()


def _validate_ws_token(token: str) -> str | None:
    try:
        parsed_id = parse_session_token(token)
    except WeChatLoginError:
        return None

    if token.startswith("device-token:"):
        return parsed_id

    cached_user_id = get_cached_auth_user_id(token)
    if cached_user_id and cached_user_id == parsed_id:
        return parsed_id

    from app.services.auth_sessions import get_active_session_by_token

    with SessionLocal() as db:
        active_session = get_active_session_by_token(db, session_token=token)
        if active_session and active_session.user.user_id == parsed_id:
            return parsed_id

    return None


@router.websocket("/ws/devices/{device_id}")
async def device_socket(
    websocket: WebSocket,
    device_id: str,
    token: str = Query(default=""),
) -> None:
    user_id = _validate_ws_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="invalid token")
        return

    await device_connections.connect(device_id=device_id, websocket=websocket)
    redis_service.set_device_online(device_id)
    await websocket.send_json(
        {
            "event": "connected",
            "device_id": device_id,
            "status": "online",
        }
    )

    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")
            notification_id = message.get("notification_id")
            if event and notification_id:
                store.register_receipt(device_id=device_id, notification_id=notification_id, event=event)
    except WebSocketDisconnect:
        device_connections.disconnect(device_id=device_id)
        redis_service.set_device_offline(device_id)
