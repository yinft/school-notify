from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.services.device_connections import device_connections
from app.services.redis_service import redis_service
from app.services.store import store
from app.services.wechat_auth import WeChatLoginError, parse_session_token


router = APIRouter()


def _validate_ws_token(token: str) -> str | None:
    if not token.startswith("device-token:"):
        return None
    try:
        return parse_session_token(token)
    except WeChatLoginError:
        return None


@router.websocket("/ws/devices/{device_id}")
async def device_socket(
    websocket: WebSocket,
    device_id: str,
    token: str = Query(default=""),
) -> None:
    token_device_id = _validate_ws_token(token)
    if not token_device_id:
        await websocket.close(code=4001, reason="invalid token")
        return
    if token_device_id != device_id:
        await websocket.close(code=4003, reason="forbidden")
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
